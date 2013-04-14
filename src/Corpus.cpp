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
#include <Corpus.hpp>

#include <fstream>
#include <sstream>

namespace pfe {

////////////////////////////////////////////////////////////////////////////////
// Corpus cover related
////////////////////////////////////////////////////////////////////////////////

OrderedDocCover fullOrderedDocCoverFromDoc(Document const& doc) {
    LongVector _indices;
    _indices.reserve(doc.size());
    for (unsigned long i=0 ; i<doc.size() ; ++i) {
        _indices.push_back(i);
    }
    return OrderedDocCover(doc.size(), _indices);
}

OrderedCover fullOrderedCoverFromCorpus(Corpus const& corpus) {
    std::map<std::string, OrderedDocCover> _map;
    for (auto i=corpus.begin() ; i!=corpus.end() ; ++i) {
        _map.insert(_map.end(),
                    {i->first, fullOrderedDocCoverFromDoc(i->second)});
    }
    return OrderedCover(_map);
}

////////////////////////////////////////////////////////////////////////////////
// Corpus parsing
////////////////////////////////////////////////////////////////////////////////

Document readDocFromStream(std::istream& is, std::string& docName) {
    Document document;
    StringVector word;

    std::string line;
    std::string token;

    std::getline(is, docName);
    std::getline(is, line);
    while (!is.eof() && !is.fail()) {
        if (line.size() == 0) {
            break;
        }
        std::stringstream ls(line);
        std::getline(ls, token, '\t');
        while (!ls.eof()) {
            std::getline(ls, token, '\t');
            word.push_back(token);
        }
        document.push_back(word);
        word.clear();

        std::getline(is, line);
    }
    return document;
}

Corpus readCorpusFromStream(std::istream& is) {
    Corpus corpus;
    std::string docName;
    Document doc;

    doc = readDocFromStream(is, docName);
    while (!is.eof() && !is.fail()) {
        corpus[docName] = doc;
        doc = readDocFromStream(is, docName);
    }
    if (corpus.find(docName) == corpus.end()) {
        corpus[docName] = doc;
    }
    return corpus;
}

Document readDocFromStr(std::string const& s, std::string& docName) {
    std::stringstream ss(s);
    return readDocFromStream(ss, docName);
}

Document readDocFromFile(std::string const& filename, std::string& docName)
throw (std::runtime_error) {
    std::ifstream fin(filename.c_str(), std::ios::in | std::ios::binary);
    if (fin.fail()) {
        std::string err = ERR_COULD_NOT_READ_FILE + filename;
        throw std::runtime_error(err.c_str());
    }
    Document doc = readDocFromStream(fin, docName);
    fin.close();
    return doc;
}

Corpus readCorpusFromStr(std::string const& s) {
    std::stringstream ss(s);
    return readCorpusFromStream(ss);
}

Corpus readCorpusFromFile(std::string const& filename)
throw (std::runtime_error) {
    std::ifstream fin(filename, std::ios::in | std::ios::binary);
    if (fin.fail()) {
        std::string err = ERR_COULD_NOT_READ_FILE + filename;
        throw std::runtime_error(err.c_str());
    }
    Corpus corpus = readCorpusFromStream(fin);
    fin.close();
    return corpus;
}

////////////////////////////////////////////////////////////////////////////////
// Corpus writing
////////////////////////////////////////////////////////////////////////////////

void writeDocToStream(std::ostream& os, Document const& doc,
std::string const& docName) {
    for (auto i=doc.begin() ; i!=doc.end() ; ++i) {
        for (auto j=i->begin() ; j<i->end() ; ++j)     {
            if (j != i->begin()) {
                os << '\t';
            }
            os << *j;
        }
        os << std::endl;
    }
}

void writeCorpusToStream(std::ostream& os, Corpus const& corpus) {
    for (auto i=corpus.begin() ; i!=corpus.end() ; ++i) {
        if (i!=corpus.begin()) {
            os << std::endl;
        }
        os << i->first << std::endl;
        writeDocToStream(os, i->second, i->first);
    }
}

void writeCorpusToFile(std::string const& filename, Corpus const& corpus)
throw (std::runtime_error) {
    std::ofstream fout(filename.c_str(), std::ios::binary | std::ios::out);
    if (!fout) {
        fout.close();
        throw std::runtime_error((ERR_COULD_NOT_WRITE_FILE + filename).c_str());
    }
    writeCorpusToStream(fout, corpus);
    fout.close();
}

Corpus
corpusSample(Corpus const& corpus, std::vector<std::string> const& docIds)
throw(std::runtime_error) {
    Corpus _sample;
    for (auto i=docIds.begin() ; i!=docIds.end() ; ++i) {
        auto j = corpus.find(*i);
        if (j == corpus.end()) {
            throw std::runtime_error(ERR_DOCUMENT_NOT_FOUND);
        } else {
            _sample[*i] = j->second;
        }
    }
    return _sample;
}

} // pfe namespace
