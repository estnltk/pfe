# -*- coding: utf-8 -*-
# Python 2.7

from pypfe import *
from random import sample

corpus = readCorpusFromFile('data/plaincorpora/ekktt_full.txt')
print 'Corpus contains {0} documents'.format(len(corpus))

radius = 2

fullcover = fullOrderedCoverFromCorpus(corpus)
rulecover = basicRuleCovers(corpus, radius)
print 'rulecover has {0} basic rules'.format(len(rulecover))

conjunctions = ConjunctionVector([Conjunction([rule]) for rule in rulecover])
print 'have {0} basic conjunctions'.format(len(conjunctions))

conjunctions = apriori(conjunctions, rulecover, fullcover, 0.05, 2, 2)

for a in conjunctions:
    cover = conjunctionCover(Conjunction(a), rulecover)
    print str(cover.metrics(fullcover).all())

