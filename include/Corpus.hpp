/*  Pattern based fact extraction library.
    Copyright (C) 2013 University of Tartu

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
#ifndef _PFE_CORPUS_HPP_
#define _PFE_CORPUS_HPP_

#include <PfeLib.hpp>
#include <Cover.hpp>

namespace pfe {

/// Define document as a vector of words. Each word is a vector of strings,
/// where each string represents an attribute of the word. The first string
/// should always be the original form of the word, but it is not required
/// to be so.
typedef std::vector<std::vector<std::string> > Document;
typedef std::map<std::string, Document> Corpus;


OrderedDocCover fullOrderedDocCoverFromDoc(Document const& doc);
OrderedCover fullOrderedCoverFromCorpus(Corpus const& corpus);

/// Read a single document from string.
/// First line of the string should contain the document name.
/// Next, each line represents a single word or punctuation mark. The word
/// can contain any number of attributes such as the POS tag etc. In that case
/// the word with its attributes should be separated by '\t' character and
/// given on a single line. For example:
///
/// Document X: Something very interesting
/// I   first_word  uppercase
/// name    lowercase
/// is  lowercase
/// Timo    uppercase named_entity
///
/// @param s: The string to read the file from.
/// @param docName: The string to store the document name.
Document readDocFromStr(std::string const& s, std::string& docName);

/// Read a single document from file specified by path.
/// @see:pfe::readDocFromStr for document format.
/// @param filename: The path of the file.
/// @param docName: The string to store the document name.
Document readDocFromFile(std::string const& filename, std::string& docName)
throw (std::runtime_error);

/// Read a corpus from string.
/// Documents should be separated by empty lines. See @see:readDocFromStr for
/// document format.
/// @param s: The string to read the file from.
Corpus readCorpusFromStr(std::string const& s);

/// Read a corpus from file specified by path.
/// Documents should be separated by empty lines. See @see:readDocFromStr for
/// document format.
/// @param filename: The path of the file.
Corpus readCorpusFromFile(std::string const& filename)
throw (std::runtime_error);

/// Write a corpus to file specified by filename.
/// File can be later read using @see:readCorpusFromFile.
void writeCorpusToFile(std::string const& filename, Corpus const& corpus)
throw (std::runtime_error);

/// Given a corpus and a list of document ids, create a subcorpus.
Corpus
corpusSample(Corpus const& corpus, std::vector<std::string> const& docIds)
throw(std::runtime_error);

} // pfe namespace

#endif // _PFE_CORPUS_HPP_

