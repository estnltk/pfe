# -*- coding: utf-8 -*-
# Python 2.7
#  Pattern based fact extraction library.
#    Copyright (C) 2013 University of Tartu
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pandas import Series, concat
from corpus import *
from wordnet import *
from itertools import izip
import tempfile
import codecs
import sys
from subprocess import PIPE, Popen
from multiprocessing import Process
import cPickle
from pdict import PersistentDict as Corpus
from copy import deepcopy

################################################################################
# Feature extraction
################################################################################

def local_bigram_features(series):
    '''Create bigram features from word series.'''
    n = len(series)
    features = [[u'bigram=' + b for b in bs] for bs in bigram_series(series)]
    return features

def local_context_features(name, series, sentence_starts, radius=2):
    '''Generate simple local context features.
    name            - the name of the feature
    series          - the datalist to generate the features for.
    sentence_starts - boolean list denoting starting positions of sentences
    radius          - how many positions before and after the token to use.
    '''
    series = list(series)
    assert (len(series) == len(sentence_starts))
    n = len(series)
    features = [[] for _ in range(n)]
    for i in range(n):
        j = i
        while not sentence_starts[j] and j > 0 and i - j < radius:
            j = j - 1
        while j < n:
            s = u'{0}[{1}]={2}'.format(name, j - i, series[j])
            features[i].append(s)
            j = j + 1
            if j == n or sentence_starts[j] or j > i + radius:
                break
    return features

def global_context_features(features, values, conditions, contexts=None):
    '''Generate simple global features.
    features   - original local context features.
    values     - equal values here will be given same global context.
    conditions - consider values, where this condition is true.
    contexts   - if given, store contexts in that particular dictionary.

    values and condition are Series objects.
    '''
    values     = list(values)
    conditions = list(conditions)
    assert (len(features) == len(values))
    assert (len(values) == len(conditions))

    # collect the global contexts in the document
    newcontexts = dict()
    n = len(features)
    for idx in range(n):
        if conditions[idx]:
            context = newcontexts.get(values[idx], set())
            context |= set(features[idx])
            newcontexts[values[idx]] = context
    # notation
    for key in newcontexts:
        newcontexts[key] = set(['glob_' + v for v in newcontexts[key]])

    # add new context to the given context, if given :)
    if contexts != None:
        for key in newcontexts:
            contexts[key] = newcontexts[key]

    # give global context to everything
    for idx in range(n):
        if conditions[idx]:
            features[idx] = set(features[idx]) | contexts[values[idx]]
        features[idx] = list(features[idx])
    return features


################################################################################
# Wrapper for CRF binary.
################################################################################

def crf_data_to_stream(stream, X, y, starts, ends):
    '''Write data to stream for crfsuite binary.'''
    for row, label, start, end in izip(X, y, starts, ends):
        toks = [label]
        toks.extend(row)
        if start:
            toks.append('__BOS__')
        if end:
            toks.append('__EOS__')
        stream.write('\t'.join(toks))
        stream.write('\n')

def prepare_crf_features(doc, **kwargs):
    '''Prepare features.

       use_wordnet - if True, then use wordnet features.
       wordnet_path - the path to wordnet database.
       use_context_aggregation - if True, create global features.
       contexts - if given, store the global contexts here.
    '''
    features = dict()
    starts = list(doc['start'])
    for col_name in doc.columns:
        if col_name not in ['end', kwargs['label']]:
            f = local_context_features(col_name, doc[col_name], starts)
            features[col_name] = f

    use_wordnet = kwargs.get('use_wordnet', False)
    wn_path     = kwargs.get('wordnet_path', 'data/wordnet.txt')

    if use_wordnet:
        wordnet = Wordnet()
        wordnet.parse(wn_path)

        features['bis'] = local_context_features('bis',
                                        wordnet.get_bis_series(doc['lemma']),
                                        starts)
        features['btc'] = local_context_features('btc',
                                        wordnet.get_btc_series(doc['lemma']),
                                        starts)
        features['hyp'] = local_context_features('hyp',
                                        wordnet.get_hyp_series(doc['lemma']),
                                        starts)

    # add some more local tracks
    features['upper'] = local_context_features('upper',
                                               uppercase_series(doc['word']),
                                               starts)
    features['aupper'] = local_context_features('allupper',
                                                all_upper_series(doc['word']),
                                                starts)
    features['bigram'] = local_bigram_features(doc['word'])

    n = len(doc)
    features = [[features[key][i] for key in features] for i in range(n)]
    features = [reduce(lambda x, y: x + y, lists) for lists in features]

    if kwargs.get('use_context_aggregation', True):
        contexts = kwargs.get('contexts', dict())
        if 'lemma' in doc.columns:
            features = global_context_features(features,
                                               doc['lemma'],
                                               uppercase_series(doc['word']),
                                               contexts)
        else:
            features = global_context_features(features,
                                               doc['word'],
                                               uppercase_series(doc['word']),
                                               contexts)
    return features

def crf_fit(corpus, **kwargs):
    doc_ids = kwargs.get('doc_ids', corpus.keys())
    label   = kwargs.get('label', 'ne_type')

    doc = concat([corpus[doc_id] for doc_id in doc_ids])
    X = prepare_crf_features(doc, **kwargs)
    y = doc[label]

    f = tempfile.NamedTemporaryFile()
    writer = codecs.getwriter('utf-8')(f)
    crf_data_to_stream(writer, X, y, doc['start'], doc['end'])
    f.seek(0)

    g = tempfile.NamedTemporaryFile()
    subprocess.call(['crfsuite', 'learn', '-m', g.name, f.name])
    g.seek(0)
    model = g.read()
    f.close()
    g.close()

    return model

def crf_predict(model, corpus, **kwargs):
    doc_ids = list(kwargs.get('doc_ids', corpus.keys()))
    label   = kwargs.get('label', 'ne_type')

    # predict document by document
    for doc_id in doc_ids:
        f = tempfile.NamedTemporaryFile()
        writer = codecs.getwriter('utf-8')(f)

        # store the original contexts
        contexts = dict()
        if 'contexts' in kwargs:
            contexts = deepcopy(kwargs['contexts'])

        doc = corpus[doc_id]
        X = prepare_crf_features(doc, **kwargs)
        y = doc[label]

        # replace the original contexts
        if 'contexts' in kwargs:
            kwargs['contexts'] = contexts

        crf_data_to_stream(writer, X, y, doc['start'], doc['end'])
        f.seek(0)

        g = tempfile.NamedTemporaryFile()
        g.write(model)
        g.seek(0)
        pipe = Popen(['crfsuite', 'tag', '-m', g.name, f.name],
                     stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, err = pipe.communicate()
        f.close()
        g.close()

        starts      = doc['start']
        ends        = doc['end']
        predictions = [p for p in out.split('\n') if len(p.strip()) >= 1]
        assert (len(starts) == len(predictions))
        assert (len(starts) == len(ends))

        yield (doc_id, Series(predictions))

def crf_model_fit(model_path, corpus, **kwargs):
    if 'contexts' not in kwargs:
        kwargs['contexts'] = dict()
    model = crf_fit(corpus, **kwargs)
    f = open(model_path, 'wb')
    cPickle.dump((model, kwargs), f)
    f.close()

def crf_model_predict(model_path, corpus, target_path, series_name):
    f = open(model_path, 'rb')
    model, kwargs = cPickle.load(f)
    f.close()
    s = Corpus(target_path)
    for doc_id, predictions in crf_predict(model, corpus, **kwargs):
        doc = corpus[doc_id]
        doc[series_name] = predictions
        s[doc_id] = doc
        sys.stderr.write('Document {0} classified.\n'.format(doc_id))
    s.close()

def crf_process(model_path, tmp_corpus_path, tmp_target_path, series_name):
    tmp_corp = Corpus(tmp_corpus_path)
    crf_model_predict(model_path, tmp_corp, tmp_target_path, series_name)
    tmp_corp.close()

def crf_model_predict_mc(model_path, corpus, target_path, series_name, n):
    '''Multi core version of crf_model_predict.
       n - number of processes to use.
    '''
    sys.stderr.write('Dividing documents between {0} processes.\n'.format(n))
    doc_ids  = list(corpus.keys())
    id_lists = [[] for _ in range(n)]
    idx = 0
    for doc_id in corpus.keys():
        id_lists[idx].append(doc_id)
        idx += 1
        if idx >= n:
            idx = 0
    sys.stderr.write('Launching processes.\n')
    dest_names   = []
    processes    = []
    for idx, ids in enumerate(id_lists):
        if len(ids) > 0:
            folder = tempfile.mkdtemp()
            # write the new corpus
            src_name  = os.path.join(folder, 'src.corpus')
            dest_name = os.path.join(folder, 'dest.corpus')
            tmp_corp = Corpus(src_name)
            tmp_corp.autocommit(False)
            for doc_id in ids:
                tmp_corp[doc_id] = corpus[doc_id]
            tmp_corp.close()

            # start the process
            process = Process(target=crf_process,
                                args=(model_path,
                                     src_name,
                                     dest_name,
                                     series_name))
            process.start()
            sys.stderr.write('Process {0} launched\n'.format(idx))
            # store the identificators
            dest_names.append(dest_name)
            processes.append(process)
    for p in processes:
        p.join()
    sys.stderr.write('Processes finished!\n')

    # concatenate temporary outputs
    target_corp = Corpus(target_path)
    target_corp.autocommit(False)
    for dest_name in dest_names:
        tmp_corp = Corpus(dest_name)
        for doc_id in tmp_corp:
            target_corp[doc_id] = tmp_corp[doc_id]
        tmp_corp.close()
    target_corp.close()
    sys.stderr.write('Corpus {0} created'.format(target_path))


