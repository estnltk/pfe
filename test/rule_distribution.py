# -*- coding: utf-8 -*-
# Python 2.7

from pypfe import *
from random import sample()

corpus = readCorpusFromFile('data/plaincorpora/ekktt_full.txt')
conjunctions = read_conjunctions('data/patterns/ekktt_005.txt')

print 'Have {0} documents and {1} conjunctions'.format(len(corpus), len(conjunctions))

radius = 2

fullcover   = fullOrderedCoverFromCorpus(corpus)
basiccovers = basicRuleCovers(corpus, radius)

metrics = conjunction_docmetrics(conjunctions, basiccovers, fullcover)
matrix  = metric_matrix(metrics, corpus.keys())

print matrix


#

conjcovers = conjunction_covers(conjunctions, basiccovers)
matrices   = matthews_matrices(conjcovers, list(sample(corpus.keys(), 2)))
