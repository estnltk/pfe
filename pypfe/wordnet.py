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

import codecs
from pandas import Series

class Wordnet(object):
    '''Simple class for reading data from wordnet.'''

    ALLOWED_RELATIONS = ['be_in_state', 'belongs_to_class', 'has_hyperonym']

    def __init__(self):
        self.synonyms  = dict()
        self.relations = dict()
        self.synsets   = dict()

    def _get_string(self, line):
        return line[line.index('"')+1 : -2].lower().strip()

    def store(self, literals, relations, pos):
        if len(literals) == 0 or len(relations) == 0:
            return

        #print (literals)
        #print (relations)

        # add synonyms
        for literal in literals:
            syns = self.synonyms.get(literal, set())
            for literal2 in literals:
                if literal == literal2:
                    syns.add(literal2)
            self.synonyms[literal] = syns

        # add relations
        for relation, rel_literal in relations:
            if relation not in self.ALLOWED_RELATIONS:
                continue
            reldata = self.relations.get(relation, dict())
            for literal in literals:
                reldata[literal] = rel_literal
            self.relations[relation] = reldata

        # add synsets
        litset = set(literals)
        for literal in litset:
            self.synsets[(pos, literal)] = litset - {literal}

    def parse(self, path):
        LITERAL     = '2 LITERAL'
        RELATION    = '2 RELATION'
        REL_LITERAL = '4 LITERAL'
        POS         = '1 PART_OF_SPEECH'

        f = codecs.open(path, 'r', 'utf-8')

        literals  = []
        relation  = None
        relations = []
        pos       = None

        line = f.readline()
        while line != '':
            if len(line.strip()) < 1:
                self.store(literals, relations, pos)
                literals  = []
                relations = []
            if LITERAL in line:
                literal = self._get_string(line)
                literals.append(literal)
            elif POS in line:
                pos = self._get_string(line)
            elif RELATION in line:
                relation = self._get_string(line)
            elif REL_LITERAL in line:
                literal = self._get_string(line)
                if relation in self.ALLOWED_RELATIONS:
                    relations.append((relation, literal))

            line = f.readline()
        f.close()

    def get_value(self, lemma, relation):
        return self.relations[relation].get(lemma, None)

    def get_bis_series(self, lemmata):
        series = [self.get_value(l, 'be_in_state') for l in lemmata]
        return Series(series)

    def get_btc_series(self, lemmata):
        series = [self.get_value(l, 'belongs_to_class') for l in lemmata]
        return Series(series)

    def get_hyp_series(self, lemmata):
        series = [self.get_value(l, 'has_hyperonym') for l in lemmata]
        return Series(series)

    def get_synonyms(self, lemmata, postags):
        assert (len(lemmata) == len(postags))
        postags = [unicode(t).lower() for t in postags]
        # translate some pos tags to english versions
        m = {'s': 'n', 'h': 'n'}
        postags = [m.get(t, t) for t in postags]
        pl = zip(postags, lemmata)
        pl = [(unicode(pos).lower(), unicode(lem).lower()) for pos, lem in pl]
        return [self.synsets.get(v, []) for v in pl]


if __name__ == '__main__':
    import sys
    wn = Wordnet()
    wn.parse(sys.argv[1])

    for tag in wn.synsets:
        print tag, wn.synsets[tag]

    print wn.get_synonyms(['TUNNETAMA', 'abImajaND'],['V', 'n'])
