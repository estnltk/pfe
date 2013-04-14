# -*- coding: utf-8 -*-
# Python 2.7

'''Simple test that just takes a PyCorpus and tries to convert stuff
from one form to another.
'''

from pypfe import *

pycorp = PyCorpus('/home/timo/projects/pfe/data/pycorpora/ekktt.corpus')
pydoc  = pycorp['5']

print pydoc

cdoc = doc_from_pydoc(pydoc, sep='???', ignore=['ne_type', 'begin'])

print cdoc
for word in cdoc:
    print tuple(word)

print 'If so far so good, let us try to convert whole ekktt corpus'

ccorp = corpus_from_pycorpus(pycorp)

print 'PyCorpus has {0} documents'.format(len(pycorp.keys()))
print ' CCorpus has {0} documents'.format(len(ccorp))

