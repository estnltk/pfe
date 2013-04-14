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
#include "Rule.hpp"

#include <boost/unordered_set.hpp>
#include <boost/unordered_map.hpp>

namespace pfe {

std::map<Rule, OrderedDocCover>
docBasicRuleCovers(Document const& document, long const radius) {
    boost::unordered_map<Rule, LongVector > _map;
    long const N = static_cast<long>(document.size());
    Rule rule;
    // enumerate the rules
    for (long idx=0 ; idx<N ; ++idx) {
        for (long offset=-radius ; offset<=radius ; ++offset) {
            long pos = idx + offset;
            if (pos<0 || pos>=N) {
                continue;
            }
            rule.first = offset;
            for (auto i=document[idx].begin(); i!=document[idx].end() ; ++i) {
                rule.second = *i;
                _map[rule].push_back(idx);
            }
        }
    }
    std::map<Rule, OrderedDocCover> _rulemap;
    for (auto i=_map.begin() ; i!=_map.end() ; ++i) {
        _rulemap[i->first] = OrderedDocCover(N, i->second);
    }
    return _rulemap;
}

std::map<Rule, OrderedCover>
basicRuleCovers(Corpus const& corpus, long const radius) {
    std::map<Rule, OrderedCover> _map;
    std::map<Rule, OrderedDocCover> _docMap;
    for (auto i=corpus.begin() ; i!=corpus.end() ; ++i) {
        std::string const& docName = i->first;
        Document const& doc        = i->second;
        _docMap = docBasicRuleCovers(doc, radius);
        for (auto j=_docMap.begin() ; j!=_docMap.end() ; ++j) {
            _map[j->first].addDocCover(docName, j->second);
        }
    }
    return _map;
}

std::set<Conjunction>
docFullConjunctions(Document const& document, long const radius) {
    std::set<Conjunction> _conjunctions;
    Conjunction _conjunction;
    long const N = static_cast<long>(document.size());
    Rule rule;
    // enumerate the rules
    for (long idx=0 ; idx<N ; ++idx) {
        _conjunction.clear();
        for (long offset=-radius ; offset<=radius ; ++offset) {
            long pos = idx + offset;
            if (pos<0 || pos>=N) {
                continue;
            }
            rule.first = offset;
            for (auto i=document[idx].begin(); i!=document[idx].end() ; ++i) {
                rule.second = *i;
                _conjunction.push_back(rule);
            }
        }
        // sort the rules in conjunction
        std::sort(_conjunction.begin(), _conjunction.end());
        _conjunctions.insert(_conjunction);
    }
    return _conjunctions;
}

std::vector<Conjunction>
fullConjunctions(Corpus const& corpus, long const radius) {
    std::set<Conjunction> _conjunctions;
    std::set<Conjunction> _docConjunctions;
    for (auto i=corpus.begin() ; i!=corpus.end() ; ++i) {
        _docConjunctions = docFullConjunctions(i->second, radius);
        _conjunctions.insert(_docConjunctions.begin(), _docConjunctions.end());
    }
    return std::vector<Conjunction>(_conjunctions.begin(), _conjunctions.end());
}

std::map<Rule, long>
docRuleCount(Document const& document, long const radius) {
    std::map<Rule, long> _map;
    long const N = static_cast<long>(document.size());
    Rule rule;
    // enumerate the rules
    for (long idx=0 ; idx<N ; ++idx) {
        for (long offset=-radius ; offset<=radius ; ++offset) {
            long pos = idx + offset;
            if (pos<0 || pos>=N) {
                continue;
            }
            rule.first = offset;
            for (auto i=document[idx].begin(); i!=document[idx].end() ; ++i) {
                rule.second = *i;
                _map[rule] += 1;
            }
        }
    }
    return _map;
}

std::map<Rule, long>
corpusRuleCount(Corpus const& corpus, long const radius) {
    std::map<Rule, long> _map;
    std::map<Rule, long> _docMap;
    for (auto i=corpus.begin() ; i!=corpus.end() ; ++i) {
        _docMap = docRuleCount(i->second, radius);
        for (auto j=_docMap.begin() ; j!=_docMap.end() ; ++j) {
            _map[j->first] += j->second;
        }
    }
    return _map;
}

std::vector<Conjunction> conjunctionPairs(std::vector<Conjunction> const& A,
                                          std::vector<Conjunction> const& B) {
    std::set<Conjunction> _conjunctions;
    std::set<Rule> _rules;
    Conjunction _conjunction;
    for (auto i=A.begin() ; i!=A.end() ; ++i) {
        for (auto j=B.begin() ; j!=B.end() ; ++j) {
            _rules.clear();
            _conjunction.clear();
            std::copy(i->begin(), i->end(),
                      std::inserter(_rules, _rules.end()));
            std::copy(j->begin(), j->end(),
                      std::inserter(_rules, _rules.end()));
            std::copy(_rules.begin(), _rules.end(),
                      std::back_inserter(_conjunction));
            _conjunctions.insert(_conjunction);
        }
    }
    std::vector<Conjunction> _result; _result.reserve(_conjunctions.size());
    _result.insert(_result.end(), _conjunctions.begin(), _conjunctions.end());
    return _result;
}

std::vector<Conjunction> uniqueConjunctions(std::vector<Conjunction> const& A) {
    boost::unordered_set<Conjunction> _conjunctions;
    std::copy(A.begin(), A.end(),
              std::inserter(_conjunctions, _conjunctions.end()));
    std::vector<Conjunction> _result; _result.reserve(_conjunctions.size());
    std::copy(_conjunctions.begin(), _conjunctions.end(),
              std::back_inserter(_result));
    return _result;
}

OrderedCover conjunctionCover(Conjunction const& c,
                            std::map<Rule, OrderedCover> const& basicCovers) {
    assert (c.size() > 0);
    std::vector<OrderedCover> _covers;
    _covers.reserve(c.size());
    for (auto i=c.begin() ; i!=c.end() ; ++i) {
        auto j = basicCovers.find(*i);
        if (j == basicCovers.end()) { // return empty cover
            OrderedCover _cov;
            return _cov;
        }
        _covers.push_back(j->second);
    }
    OrderedCover _cov = _covers[0];
    for (unsigned int i=1 ; i<_covers.size() ; ++i) {
        _cov &= _covers[i];
    }
    return _cov;
}

std::vector<Conjunction>
reorderRecall(std::vector<Conjunction> const& conjunctions,
              std::map<Rule, OrderedCover> const& basicCovers,
              OrderedCover const& trueCover)
{
    std::vector<std::pair<double, long> > _buffer;
    _buffer.reserve(conjunctions.size());
    // compute the recalls
    for (size_t idx=0 ; idx<conjunctions.size() ; ++idx) {
        OrderedCover c = conjunctionCover(conjunctions[idx], basicCovers);
        auto metrics = c.metrics(trueCover);
        _buffer.push_back({metrics.recall(), idx});
    }
    // sort according to recall decreasingly
    std::sort(_buffer.begin(), _buffer.end(),
              std::greater<std::pair<double, long> >());
    std::vector<Conjunction> _result;
    // copy and return conjunctions
    _result.reserve(_buffer.size());
    for (auto i=_buffer.begin() ; i!=_buffer.end() ; ++i) {
        _result.push_back(conjunctions[i->second]);
    }
    return _result;
}

} // namespace pfe
