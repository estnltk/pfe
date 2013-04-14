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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Program for converting PyCorpus to C++ corpus.')
    parser.add_argument('pycorp', type=str, help='Path of the Python corpus to read.')
    parser.add_argument('corp', type=str, help='Path of the C++ corpus to write.')
    parser.add_argument('--sep', type=str, default='=', help='Attribute name and value separator in C++ corpus. (default =)')
    parser.add_argument('--ignore', type=str, nargs='*', help='Attribute names to ignore (optional)')
    parser.add_argument('--wordnet', type=str, default='', help='Path to wordnet dictionary to extract wordnet features (optional)')
    parser.add_argument('--local', type=bool, default=False, help='If specified, extract additional local features as well.')

    args = parser.parse_args()
    if not os.path.exists(args.pycorp):
        sys.stderr.write('{0} does not exist!\n'.format(args.pycorp))
        sys.exit(1)

    sys.stderr.write('Loading {0}\n'.format(args.pycorp))
    pycorp = PyCorpus(args.pycorp)
    sys.stderr.write('Converting ...')
    corp = corpus_from_pycorpus(pycorp,
                                sep=args.sep,
                                ignore=args.ignore,
                                wordnetpath=args.wordnet,
                                local=args.local)
    sys.stderr.write('done\n')
    sys.stderr.write('Writing to path {0}'.format(args.corp))
    writeCorpusToFile(args.corp, corp)
    sys.stderr.write(' done!\n')
