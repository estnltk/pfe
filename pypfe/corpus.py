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

'''
Corpus module.

Deals with parsing and converting corpora between different formats. Also
contains other minor functionality.

Note that the internal corpus format is given in C++ while methods described
here provide additional functionality such as named attributes.
'''

import pandas
from pandas import Series, DataFrame, ExcelFile, ExcelWriter
import nltk
from nltk.stem.snowball import EnglishStemmer, SpanishStemmer
import codecs
import re
import sys
import os
import string
from itertools import izip
import subprocess
import tempfile
import cPickle
from pdict import PersistentDict as PyCorpus
import cStringIO
import numpy as np
import xlrd
import math

from pfe import *
from wordnet import Wordnet

################################################################################
# Functions for converting between Corpus and PyCorpus
################################################################################

def doc_from_pydoc(doc, **kwargs):
    '''Convert a single document of PyCorpus to C++ document.
    One main difference is that C++ corpus does not have named attributes.
    Therefore we convert these to single attributes
    `attr_name``sep``attr_value`.

    keyword arguments:
        sep - what string to use for separating attribute names and values.
        ignore - list of attribute names to ignore. For example `ne_type` might
            not be useful for converting corpus to mine data for named entity
            classification, if that attribute is not available in test corpora.
        wordnetpath - if specified, then extract basic wordnet features.
        local - if specified and True, then extract additionally extra local
                features.
        bigram - if specified and True, then extract also word bigrams.
    '''
    sep      = kwargs.get('sep', '=')
    ignore   = kwargs.get('ignore', [])
    local    = kwargs.get('local', False)
    bigram   = kwargs.get('bigram', False)
    wordnetpath = kwargs.get('wordnetpath', '')
    colnames = list(set(doc.columns) - set(ignore))
    rows     = doc.index
    words    = []
    # local features
    uppercase    = []
    alluppercase = []
    bigrams      = []
    digits       = []
    punct        = []
    # external features
    synonyms     = []

    if local:
        uppercase    = [unicode(t) for t in uppercase_series(doc.word)]
        alluppercase = [unicode(t) for t in all_upper_series(doc.word)]
        digits       = [unicode(t) for t in contains_digit_series(doc.word)]
        punct        = [unicode(t) for t in contains_punct_series(doc.word)]
    if bigram:
        bigrams      = [unicode(t) for t in bigram_series(doc.word)]
    wn = Wordnet()
    if len(wordnetpath) > 0:
        wn.parse(wordnetpath)
        synonyms = wn.get_synonyms(doc.lemma, doc.wtype)
    for row in rows:
        data = [unicode(col) + sep + unicode(doc[col][row]) for col in colnames]
        # extract local features
        if local:
            data.append('upper' + sep + uppercase[row])
            data.append('allupper' + sep + alluppercase[row])
            data.append('hasdigit' + sep + digits[row])
            data.append('haspunct' + sep + punct[row])
        if bigram:
            for bg in bigrams[row].split():
                data.append('bigram' + sep + bg)
        # extract wordnet features
        if len(wordnetpath) > 0:
            for synonym in synonyms[row]:
                data.append('synonym' + sep + synonym)
        data = [codecs.encode(v, 'utf-8') for v in data]
        word = StringVector(data)
        words.append(word)
    return Document(words)

def uppercase_series(words):
    return Series([w[:1].istitle() for w in words])

def all_upper_series(words):
    return Series([w.isupper() for w in words])

def bigram_series(words):
    return Series([' '.join([l + r for l, r in zip(w.lower(), w[1:].lower())])
                    for w in words])

def contains_digit_series(words):
    digs = set(string.digits)
    return Series([len(set(word) & digs) > 0 for word in words])

def contains_punct_series(words):
    digs = set(string.punctuation)
    return Series([len(set(word) & digs) > 0 for word in words])

def corpus_from_pycorpus(pycorpus, **kwargs):
    '''Convert a PyCorpus instance to Corpus instance.
    keyword arguments:
        sep - what string to use for separating attribute names and values.
        ignore - list of attribute names to ignore. For example `ne_type` might
            not be useful for converting corpus to mine data for named entity
            classification, if that attribute is not available in test corpora.
        wordnetpath - if specified, then extract basic wordnet features.
        local - if specified and True, then extract additionally extra local
                features.
        bigram - if specified and True, then extract also word bigrams.
    '''
    data = {}
    for doc_name in pycorpus.keys():
        data[doc_name] = doc_from_pydoc(pycorpus[doc_name], **kwargs)
    return Corpus(data)

################################################################################
# Parsing plain text corpora
################################################################################

def sentence_splitter(lineiter):
    '''From a generator of lines, create a generator of sentences.'''
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    for line in lineiter:
        for sentence in sent_detector.tokenize(line.strip()):
            yield sentence

def line_iterator(file_obj):
    '''Given a file object, create a line generator.'''
    line = file_obj.readline()
    while line != '':
        yield line
        line = file_obj.readline()

def parse_plain_doc(path):
    '''Parse a plain text corpus from a file.'''
    f = codecs.open(path, 'rb', 'utf-8')
    doc = parse_plain_doc_from_stream(f)
    f.close()
    return doc

def parse_plain_doc_from_stream(stream):
    '''Parse a plain text corpus from a stream.'''
    ss = sentence_splitter(line_iterator(stream))
    words  = []; starts = []; ends   = []
    word_tokenizer = nltk.PunktWordTokenizer()
    for s in ss:
        ws = word_tokenizer.tokenize(s)
        words.extend(ws)
        if len(ws) >= 1:
            starts.append(True)
            starts.extend([False]*(len(ws) - 1))
            ends.extend([False]*(len(ws) - 1))
            ends.append(True)
    return DataFrame({'word': words,
                      'start': starts,
                      'end': ends})

def parse_plain_corpus(plainpath, corpuspath):
    corpus = PyCorpus(corpuspath)
    data = codecs.open(plainpath, 'rb', 'utf-8').read()
    docs = re.split('s*?\r?\n\r?\n', data)
    data = None
    corpus.autocommit(False)
    for doc in docs:
        lines = re.split('\r?\n', doc.strip())
        title = lines[0].strip()
        contents = '\n'.join(lines[1:]).strip()
        text_stream = cStringIO.StringIO(contents.encode('utf-8'))
        utf8_stream = codecs.getreader('utf-8')(text_stream)
        corpus[title] = parse_plain_doc_from_stream(utf8_stream)
    corpus.commit()
    corpus.close()


################################################################################
# Parsing Wikipedia corpora created with WikiExtractor.py
################################################################################

def parse_wikipedia(path, corpus_path):
    '''path - the directory containing the extracted documents by
       WikiExtractor.py.
       corpus_path - the filename to store the parsed corpus.
    '''
    corpus = PyCorpus(corpus_path)

    def from_path(path):
        sys.stderr.write('Processing path ' + path + '\n')
        files = os.listdir(path)
        for f in files:
            newpath = os.path.join(path, f)
            if os.path.isdir(newpath):
                from_path(newpath)
            else:
                sys.stderr.write('Processing file ' + newpath + '\n')
                get_documents(newpath)

    def get_documents(path):
        f = codecs.open(path, 'r', 'utf-8')
        contents = f.read()
        f.close()
        doctexts  = contents.split('<doc id="')
        documents = []

        for text in doctexts:
            text = text.strip()
            if len(text) < 1:
                continue
            # extract the document parts
            doc_id = int(text[:text.index('"')])
            title  = text[text.index('title="')+7 : text.index('"', text.index('title="')+7)]
            text   = text[text.index('\n') : text.index('</doc>')].strip()

            text_stream = cStringIO.StringIO(text.encode('utf-8'))
            utf8_stream = codecs.getreader('utf-8')(text_stream)
            corpus[str(doc_id)] = parse_plain_doc_from_stream(utf8_stream)
        return documents

    from_path(path)

    corpus.sync()
    return corpus


################################################################################
# Parsing t3mesta corpora
################################################################################

class T3Data(object):
    '''Parser for t3mesta output with optional ner type column
    '''

    word_types = set(['S', 'V', 'C', 'H', 'K', 'D', 'N', 'Z', 'U', 'J', 'Y',
                      'I', 'P', 'A', 'O', 'X', 'G'])
    cases      = set(['n', 'g', 'p', 'ill', 'in', 'el', 'all', 'ad', 'abl',
                      'tr', 'ter', 'es', 'ab', 'kom', 'adt'])
    verb_types = set(['n', 'd', 'b',    # mina teen, sina teed, tema teeb
                  'me', 'te', 'vad',    # meie teeme, teie teete, nemad teevad
                  'sin', 'sid', 's',    # mina tegin, sina tegid, tema tegi
                  'sime', 'site', 'sid',# meie tegime, teie tegite, nemad tegid
                  'ma', 'mas', 'mast',  # tegema, tegemas, tegemast
                  'ti', 'taks', 'takse',# midagi tehti, midagi tehtaks, tehakse
                  'o', 'ge',  'gem',    # tee seda, tehke seda, tehkem seda
                  'vat', 'maks', 'tagu',# olevat, selgitamaks, langetagu
                  'nuks', 'tavat',      # laulnuks, kahtlustatavat
                  'nuksin', 'tav',      # laulnuksin, arvutatav
                  'nuksid', 'v',        # laulnuksid, seonduma,
                  'nuksime', 'nuvat',   # saanuksime, põletanuvat?
                  'tuks',               # koormatuks
                  'tud', 'nud', 'da',   # tehtud laps, jooksnud mees, teha
                  'des', 'ks', 'ksin',  # tehes midagi, teeks midagi, teeksin
                  'ksite', 'ksime',     # teeksite midagi, teeksime midagi
                  'ksid', 'gu', 'mata', # teeksid midagi, tehku, tegemata
                  'ksime', 'tama', 'ta' # teeksime midagi, langetama puid, saada
                  ])

def parse_t3_doc(path):
    '''Parse a t3 document from path.'''
    f = codecs.open(path, 'rb', 'utf-8')
    doc = parse_t3_doc_from_stream(f)
    f.close()
    return doc

def parse_t3_doc_from_stream(stream):
    '''Parse a t3 document from stream.'''
    sentences = read_t3_sentences(stream)
    # (orig, lemma, wtype, case, plur, vtype, negation, label)
    doc = [[] for _ in range(8)]
    starts = []; ends = []
    for idx, s in enumerate(sentences):
        series = zip(*s)
        doc[0].extend(series[0])
        doc[1].extend(series[1])
        doc[2].extend(series[2])
        doc[3].extend(series[3])
        doc[4].extend(series[4])
        doc[5].extend(series[5])
        doc[6].extend(series[6])
        doc[7].extend(series[7])
        ends.extend([False]*(len(series[0])-1))
        if len(series[0]) > 0:
            starts.append(True)
            ends.append(True)
        starts.extend([False]*(len(series[0])-1))
    return DataFrame({'word': doc[0],
                      'lemma': doc[1],
                      'wtype': doc[2],
                      'case': doc[3],
                      'plur': doc[4],
                      'vtype': doc[5],
                      'negation': doc[6],
                      'ne_type': doc[7],
                      'start': starts,
                      'end': ends})

def parse_t3_doc_from_string(string):
    plain_stream = cStringIO.StringIO(string.encode("utf-8"))
    utf_stream   = codecs.getreader('utf-8')(plain_stream)
    return parse_t3_doc_from_stream(utf_stream)

def read_t3_sentences(stream):
    sentences = []
    sentence = read_t3_sentence(stream)
    while sentence != []:
        sentences.append(sentence)
        sentence = read_t3_sentence(stream)
    return sentences

def read_t3_sentence(stream):
    sentence = []
    word = read_t3_word(stream)
    while word != None:
        sentence.append(word)
        word = read_t3_word(stream)
    return sentence

def read_t3_word(stream):
    # read next line
    line = stream.readline().strip()
    if line == '':
        return None

    # t3mesta attributes are separated by tabs
    tokens = [token.strip() for token in line.split('\t')]
    if len(tokens) < 3:
        raise Exception('Could not read line {0}'.format(line))

    # get the attributes and create the word representation
    attributes = get_t3_attributes(tokens[2])

    # extract basic features
    orig      = tokens[0]
    lemma     = fix_t3_lemma(tokens[1])
    wtype     = get_t3_word_type(attributes)
    label = ''
    if len(tokens) == 4:
        label     = get_t3_label(tokens[3])

    # extract other features
    case     = None
    plur     = None
    negation = None
    vtype    = None

    if wtype == 'V':
        negation = get_t3_negation(attributes)
        vtype    = get_t3_verb_type(attributes)
        if vtype == None and negation == False:
            uwriter = codecs.getwriter('utf-8')(sys.stderr)
            uwriter.write(u'WARNING: Invalid verb {0}\n'.format(line))
    else:
        case = get_t3_case(attributes)
        plur = get_t3_plurality(attributes)

    # put together the word instance
    word = (orig, lemma, wtype, case, plur, vtype, negation, label)
    return word

def fix_t3_lemma(lemma):
    '''Keep only the canonical form of the lemma i.e. remove all the additional
       notation.
    '''
    lemma = lemma.strip().lower()
    if len(lemma) > 1:
        lemma = lemma.replace('_', '').replace('=', '')
        try:
            idx = lemma.index('+')
            if idx != -1 and idx != 0:
                lemma = lemma[:idx]
        except ValueError:
            pass
    return lemma

def get_t3_attributes(attributes):
    '''Get the list of attributes from t3mesta format for the word.
    Function removes pipe and underscore characters (used in pfe program)
    from the attributes automatically.
    '''
    attrs = []
    for attr in attributes.split():
        attr = attr.strip().replace('|', '').replace('_', '')
        attrs.append(attr)
    return attrs

def get_t3_word_type(attributes):
    '''Extract the word type from given attributes.
    '''
    for attr in attributes:
        if attr in T3Data.word_types:
            return attr
    return None

def get_t3_case(attributes):
    '''Extract the case from given attributes.
    '''
    for attr in attributes:
        if attr in T3Data.cases:
            return attr
    return None

def get_t3_plurality(attributes):
    '''Get the plurality from given attributes.
    '''
    for attr in attributes:
        if attr == 'sg':
            return 'sg'
        elif attr == 'pl':
            return 'pl'
    return None

def get_t3_verb_type(attributes):
    '''Get the verb type from given attributes.sg g
    '''
    for attr in attributes:
        if attr in T3Data.verb_types:
            return attr
    return None

def get_t3_negation(attributes):
    '''get the negation from given attributes.
    '''
    for attr in attributes:
        if attr == 'neg':
            return True
    return False

def get_t3_label(label):
    '''Get the annotated label from given attributes.
    If attribute is prefixed with "B-", it is removed and the value without
    the prefix is returned.
    '''
    if label[:2] in ['B-', 'I-']:
        return label[2:]
    return label

def as_t3doc(doc):
    '''Convert any document to t3 document. Uses only words and start end
       series from the input document.'''
    SEP = '\n**********\n'
    # analyze the code with t3mesta
    f = tempfile.TemporaryFile()
    g = codecs.getwriter('utf-8')(f, 'strict')
    first = True
    for word, start, end in izip(doc['word'], doc['start'], doc['end']):
        if start and not first:
            f.write(SEP)
        first = False
        g.write(word + ' ')
    g.flush()
    f.flush()
    f.seek(0)
    p = subprocess.Popen(['t3mesta', '-cio', 'utf8', '+1'],
                         stdin=f,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    out = unicode(out, 'utf-8')
    f.close()
    # convert and separate sentences
    f = tempfile.TemporaryFile()
    g = codecs.getwriter('utf-8')(f, 'strict')
    for line in out.strip().split('\n'):
        print line
        if line.startswith('**********'):
            g.write('\n')
            continue
        parts = line.split()
        if len(parts) >= 3:
            word, lemma = parts[:2]
            attrs = u' '.join(parts[2:])
            i = attrs.find('//')
            j = attrs.find('//', i+2)
            attrs = attrs[i:j]
            attrs = string.replace(attrs.strip(), '/', '')
            attrs = string.replace(attrs, '_', '')
            attrs = string.replace(attrs, ',', '')
            g.write(u'{0}\t{1}\t{2}\t\n'.format(word, lemma, attrs))
    g.flush(); f.flush()
    # now parse it with t3mesta parser
    f.seek(0)
    doc = parse_t3_doc_from_stream(codecs.getreader('utf-8')(f, 'strict'))
    f.close()
    return doc

def as_t3corpus(orig_path, t3_path):
    '''Convert a corpus at orig_path to t3mesta corpus to t3_path.'''
    orig_corpus = PyCorpus(orig_path)
    dest_corpus = PyCorpus(t3_path)
    dest_corpus.autocommit(False)

    dest_keys = set(dest_corpus.keys())
    for key in orig_corpus.keys():
        if key not in dest_keys:
            dest_corpus[key] = as_t3doc(orig_corpus[key])

    dest_corpus.commit()

    orig_corpus.close()
    dest_corpus.close()

def boi_to_t3corpus(orig_path, t3_path):
    '''Parse a t3 corpus, where documents are separated with -- '''
    f = codecs.open(orig_path, 'rb', 'utf-8')
    contents = f.read()
    f.close()
    docs = re.split('--\r?\n\r?\n', contents)
    corpus = PyCorpus(t3_path)
    for i, doc in enumerate(docs):
        corpus[str(i+1)] = parse_t3_doc_from_string(doc)
    corpus.close()

################################################################################
# Creating POS-tagged corpora for various other languages.
################################################################################

def as_eng_postagged_doc(doc):
    '''Uses nltk default tagger.'''
    tags    = [t for _, t in nltk.pos_tag(list(doc.word))]
    stemmer = EnglishStemmer()
    lemmata = [stemmer.stem(w) for w in list(doc.word)]
    doc['pos']   = Series(tags)
    doc['lemma'] = Series(lemmata)
    return doc

def as_eng_postagged_corpus(orig_path, eng_path):
    '''Uses nltk default tagger.'''
    assert (orig_path != eng_path)
    orig = PyCorpus(orig_path)
    dest = PyCorpus(eng_path)
    dest.autocommit(False)
    for doc_id in orig.keys():
        dest[doc_id] = as_eng_postagged_doc(orig[doc_id])
    dest.commit()
    orig.close()
    dest.close()

def as_treetagger_doc(doc, encoding='latin-1', language='english'):
    '''Use treetagger for tagging the documents. Note that
    encoding `utf-8` is specified as `utf8` (different from Python notation).
    '''
    tg = TreeTagger(encoding=encoding, language=language)
    output = tg.tag(list(doc.word))
    tags    = [t[1] for t in output]
    lemmata = [fix_t3_lemma(t[2]) for t in output]
    doc['pos']   = Series(tags)
    doc['lemma'] = Series(lemmata)
    return doc

def as_treetagger_corpus(orig_path, dest_path, encoding='latin-1', language='english'):
    assert (orig_path != eng_path)
    orig = PyCorpus(orig_path)
    dest = PyCorpus(eng_path)
    dest.autocommit(False)
    for doc_id in orig.keys():
        dest[doc_id] = as_treetagger_doc(orig[doc_id], encoding=encoding, language=language)
    dest.commit()
    orig.close()
    dest.close()

################################################################################
# Subcorpus class.
################################################################################

class SubPyCorpus(PyCorpus):
    '''Subcorpus meant for reading. Does not create new files.'''

    def __init__(self, *args, **kwargs):
        self.subkeys = []
        if 'keys' in kwargs:
            self.subkeys = set(kwargs['keys'])
            del kwargs['keys']
        PyCorpus.__init__(*args, **kwargs)

    def __getitem__(self, key):
        if key in self.subkeys:
            return PyCorpus.__getitem__(self, key)
        raise KeyError()

    def __setitem__(self, key, value):
        raise Exception('SubPyCorpus does not allow writing elements.')

    def __delitem__(self, key):
        raise Exception('SubPyCorpus does not allow deleting elements.')

    def keys(self):
        return self.subkeys


################################################################################
# Load/save/import/export/convert documents/corpora
# Ordinarily, the corpora are stored as shelves of DataFrames
################################################################################

def save_doc(path, doc):
    '''Save a single document (DataFrame) as CSV file.'''
    f = open(path, 'w')
    doc.to_csv(f, encoding='utf-8')
    f.close()

def load_doc(path):
    '''Load a csv file as a DataFrame.'''
    return pandas.read_csv(path, encoding='utf-8')

def corpus_to_excel(corpus_path, excel_path):
    '''NB! Make sure to use .xls file extension for Excel files.'''
    corpus = PyCorpus(corpus_path)
    writer = ExcelWriter(excel_path)
    for key in corpus:
        corpus[key].to_excel(writer, sheet_name=key)
    writer.save()
    corpus.close()

def excel_to_corpus(excel_path, corpus_path):
    '''NB! Make sure to use .xls file extension for Excel files.'''
    corpus = PyCorpus(corpus_path)
    excel  = ExcelFile(excel_path)
    # as we do not know the number of sheets, we parse all of them
    # until we obtain a error
    idx = 0
    while True:
        try:
            df = excel.parse(str(idx))
            # recreate some information that was modified when exporting to xls
            new_df = dict()
            for col in df.columns:
                data = []
                for v in df[col]:
                    if type(v) == float and math.isnan(v):
                        data.append(None)
                    elif v == 0:
                        data.append(False)
                    elif v == 1:
                        data.append(True)
                    else:
                        data.append(v)
                new_df[col] = Series(data)
            corpus[str(idx)] = DataFrame(new_df)
        except xlrd.biffh.XLRDError:
            break
        idx += 1
    corpus.close()

################################################################################
# Ways to spice up the corpora with simple local features
################################################################################

def uppercase_series(words):
    return Series([w[:1].istitle() for w in words])

def all_upper_series(words):
    return Series([w.isupper() for w in words])

def bigram_series(words):
    return Series([' '.join([l + r for l, r in zip(w.lower(), w[1:].lower())])
                    for w in words])

def contains_digit_series(words):
    digs = set(string.digits)
    return Series([len(set(word) & digs) > 0 for word in words])

################################################################################
# Generic helper functions
################################################################################

def split_list(l, splits):
    '''Split a list of elements into multiple lists.
       splits should be a list-like object containing boolean values, where
       True value marks a splitting point.
    '''
    assert (len(l) == len(splits))
    n = len(l)
    res     = []
    current = []
    for idx in range(n):
        current.append(l[idx])
        if splits[idx]:
            res.append(current)
            current = []
    if len(current) > 0:
        res.append(current)
    return res

################################################################################
# Cover related stuff
################################################################################

def regex_doc_cover(words, pattern):
    '''Given a series of words and a regular expression, create an
    OrderedDocCover instance.'''
    words = [unicode(word) for word in words]
    idxs  = []
    for idx, word in enumerate(words):
        if idx > 0:
            idxs.append(idx)
        idxs.extend([idx]*len(word))
    s = u' '.join(words)
    cover = set()
    for mg in re.finditer(pattern, s):
        for idx in range(mg.start(), mg.end()):
            cover.add(idxs[idx])
    return OrderedDocCover(len(words), LongVector(list(frozenset(cover))))

def regex_cover(corpus, series_name, pattern):
    cover = OrderedCover()
    for doc_id in corpus.keys():
        odc = regex_doc_cover(corpus[doc_id][series_name], pattern)
        cover.addDocCover(doc_id, odc)
    return cover



''' Deprecated'''

def tuple_cover(cover):
    '''Convert a corpus cover to tuple cover.

    Corpus cover is a dictionary, where keys represent document ids.
    Tuple cover is a set of (doc_id, idx) elements.'''
    return frozenset([(doc_id, i) for doc_id in cover for i in cover[doc_id]])

def consequent_cover(cover):
    elems = list(sorted(cover))
    n = len(elems)
    newcover = set()
    i = 0
    while i < n:
        j = i
        while j < n and elems[j] - elems[i] == j - i:
            j += 1
        newcover.add((elems[i], elems[j-1]+1))
        i = j
    return frozenset(newcover)

def consequent_cover_corpus(cover):
    '''Convert cover elements denoting consequent elements as
       tuple(begin, end).'''
    new_cover = dict()
    for key in cover:
        new_cover[key] = consequent_cover(cover[key])
    return new_cover

def cover_size(cover):
    return sum(len(cover[key]) for key in cover)

def context_cover(cover, radius=2):
    c_cover = set()
    for start, end in cover:
        c_cover.add((start-2, end+2))
    return frozenset(c_cover)

def context_cover_corpus(cover, radius=2):
    c_cover = dict()
    for doc_id in cover:
        c_cover[doc_id] = context_cover(cover[doc_id], radius)
    return c_cover

def extract_series(doc, series_name, cover):
    series = doc[series_name]
    parts  = []
    for start, end in cover:
        parts.append(Series(list(series[start:end])))
    return parts

def extract_series_corpus(corpus, series_name, cover):
    series = dict()
    for doc_id in cover:
        doc = corpus[doc_id]
        series[doc_id] = extract_series(doc, series_name, cover[doc_id])
    return series

