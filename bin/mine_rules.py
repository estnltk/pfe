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

from pypfe import *
import sys
import argparse
import os
from random import sample

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Program for mining high recall patterns.')
    parser.add_argument('corp', type=str, help='Path of the C++ corpus to read.')
    parser.add_argument('type',type=str,choices=['recall', 'fprate'])
    parser.add_argument('treshold',type=float, help='Treshold.')
    parser.add_argument('--radius',type=int,default=2,help='Context radius of the patterns.')
    parser.add_argument('--threads', type=int,default=1,help='Number of threads to use.')
    parser.add_argument('--limit',type=int,default=2,help='Max number of iterations in Apriori..')
    parser.add_argument('--samplesize',type=int,default=0,help='If given, take random `samplesize` doucuments from corpus.')

    args = parser.parse_args()
    if not os.path.exists(args.corp):
        print '{0} does not exist!'.format(args.corp)
        sys.exit(1)

    if args.treshold < 0 or args.treshold > 1:
        print 'Treshold should be in range [0,1]'
        sys.exit(0)

    if args.limit == 0:
        print 'limit should be at least 1'
        sys.exit(0)

    if args.threads == 0:
        print 'number of theads should be at least 1'
        sys.exit(0)

    corpus = readCorpusFromFile(args.corp)
    sys.stderr.write('Corpus contains {0} documents\n'.format(len(corpus)))

    if args.samplesize < 0:
        print 'Samplesize must be positive integer'
        sys.exit(0)
    elif args.samplesize > 0:
        n = min(len(corpus), args.samplesize)
        names = sample(corpus.keys(), len(corpus) - n)
        for name in names:
            del corpus[name]

    sys.stderr.write('Corpus contains {0} documents after sampling\n'.format(len(corpus)))

    fullcover = fullOrderedCoverFromCorpus(corpus)
    rulecover = basicRuleCovers(corpus, args.radius)
    sys.stderr.write('There are {0} basic rules\n'.format(len(rulecover)))

    conjunctions = []
    if args.type == 'recall':
        conjunctions = ConjunctionVector([Conjunction([rule]) for rule in rulecover])
        sys.stderr.write('Have {0} basic conjunctions\n'.format(len(conjunctions)))
    elif args.type =='fprate':
        conjunctions = ConjunctionVector(fullConjunctions(corpus, args.radius))

    method = hrApriori
    if args.type == 'fprate':
        method = hpApriori
        sys.stderr.write('Mining high precision rules fprate<={0}\n'.format(args.treshold))
    else:
        sys.stderr.write('Mining high recall rules recall=>{0}\n'.format(args.treshold))

    conjunctions = method(conjunctions, rulecover, fullcover,
                          args.treshold, args.limit, args.threads)

    for a in conjunctions:
        for idx, c in enumerate(a):
            if idx > 0:
                sys.stdout.write('\t')
            sys.stdout.write('{0}\t{1}'.format(c[0], c[1]))
        sys.stdout.write('\n')

