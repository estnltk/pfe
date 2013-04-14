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
#ifndef _PFE_COVER_HPP_
#define _PFE_COVER_HPP_

#include <PfeLib.hpp>
#include <DocCover.hpp>

//todo: implement cumulative cover ordering
//todo: perform a study comparing using ordered vs bitset covers in data mining

namespace pfe {

/// Cover represents a cover in a whole corpus or subcorpus.
/// @tparam T: What document cover to use internally.
template<class T>
class Cover {
    /// Mapping of document names to their respective covers.
    typedef std::map<std::string, T> _maptype;
    _maptype _map;
public:
    /// Construct an empty cover.
    Cover() { }
    /// Copy constructor
    Cover(Cover const& other) : _map(other._map) { }
    /// Create cover from an standard map
    Cover(std::map<std::string, T> const& m);
    /// Convert the cover to standard map.
    std::map<std::string, T> map() const;
    /// Add a new document to the cover.
    void addDocCover(std::string const& docName, T const& cover)
    throw(std::runtime_error);
    /// Get the names of the cover documents.
    StringVector names() const;
    /// Return the DocCover instance given by document name.
    T docCover(std::string const& docName) const
    throw (std::range_error);
    /// Return the size of the corpus.
    size_t size() const;
    /// Given a list of document covers, create a subcover containing only
    /// those documents.
    Cover<T> sample(std::vector<std::string> const& docIds);
    /// Given a true cover (or other cover), compute the metrics object
    /// that can be used to get the precision, recall etc.
    CoverMetrics metrics(Cover<T> const& trueCover) const
    throw(std::runtime_error);
    /// Given a true cover (or other cover), compute the metrics object
    /// that can be used to get the precision, recall etc. But do it for
    /// all individual documents
    std::map<std::string, CoverMetrics>
    documentMetrics(Cover<T> const& trueCover) const throw(std::runtime_error);
    /// Compare equality of two covers.
    bool operator==(Cover<T> const& other) const;
    bool operator!=(Cover<T> const& other) const;
    /// Perform a cover intersection.
    /// Only documents present in both cover well be in the result.
    /// Those documents have intersected cover elements.
    Cover<T> const& operator&=(Cover<T> const& other)
    throw(std::runtime_error);
    /// Perform a cover union.
    /// Documents of both covers will be present in the result and matching
    /// document cover elements will be unioned.
    Cover<T> const& operator|=(Cover<T> const& other)
    throw(std::runtime_error);
    /// Perform a cover difference.
    Cover<T> const& operator-=(Cover<T> const& other)
    throw(std::runtime_error);
    /// Perform a cover symmetric difference.
    Cover<T> const& operator^=(Cover<T> const& other)
    throw(std::runtime_error);
    Cover<T> operator&(Cover<T> const& other);
    Cover<T> operator|(Cover<T> const& other);
    Cover<T> operator-(Cover<T> const& other);
    Cover<T> operator^(Cover<T> const& other);
};

typedef Cover<OrderedDocCover> OrderedCover;
typedef Cover<BitsetDocCover> BitsetCover;

template<class T> Cover<T>::Cover(std::map<std::string, T> const& m) {
    for (auto i=m.begin() ; i!=m.end() ; ++i) {
        _map[i->first] = i->second;
    }
}

template<class T> std::map<std::string, T> Cover<T>::map() const {
    std::map<std::string, T> m;
    for (auto i=_map.begin() ; i!=_map.end() ; ++i) {
        m[i->first] = i->second;
    }
    return m;
}

template<class T> void Cover<T>::addDocCover(std::string const& docName,
        T const& cover)
throw(std::runtime_error) {
    auto i = _map.find(docName);
    if (i != _map.end()) {
        throw std::runtime_error(ERR_DOC_WITH_NAME_EXIST);
    }
    _map.insert(i, {docName, cover});
}

template<class T> StringVector Cover<T>::names() const {
    StringVector v;
    v.reserve(_map.size());
    for (auto i=_map.begin() ; i!=_map.end() ; ++i) {
        v.push_back(i->first);
    }
    std::sort(v.begin(), v.end());
    return v;
}

template<class T> T Cover<T>::docCover(std::string const& docName) const
throw (std::range_error) {
    auto i = _map.find(docName);
    if (i == _map.end()) {
        throw std::range_error(ERR_DOC_NOT_FOUNT);
    }
    return i->second;
}

template<class T> size_t Cover<T>::size() const {
    size_t s = 0;
    for (auto i=_map.begin() ; i!=_map.end() ; ++i) {
        s += i->second.size();
    }
    return s;
}

template<class T>
Cover<T> Cover<T>::sample(std::vector<std::string> const& docIds) {
    Cover<T> _sample;
    for (auto i=docIds.begin() ; i!=docIds.end() ; ++i) {
        auto j=_map.find(*i);
        if (j==_map.end()) {
            continue; // empty document covers may not be represented
            //throw std::runtime_error(ERR_DOCUMENT_NOT_FOUND);
        }
        _sample.addDocCover(j->first, j->second);
    }
    return _sample;
}

template<class T> CoverMetrics
Cover<T>::metrics (Cover<T> const& trueCover) const throw(std::runtime_error) {
    long tp = 0;
    long fp = 0;
    long tn = 0;
    long fn = 0;
    for (auto i=_map.begin() ; i!=_map.end() ; ++i) {
        auto j = trueCover._map.find(i->first);
        // if second cover is not found, assume it is empty
        if (j == trueCover._map.end()) {
            fp += i->second.size();
            //throw std::range_error(ERR_DOC_NOT_FOUNT);
        } else {
            CoverMetrics m = i->second.metrics(j->second);
            tp += m.tp();
            fp += m.fp();
            tn += m.tn();
            fn += m.fn();
        }
    }
    // documents that are in second cover but not in first are false negatives
    for (auto j=trueCover._map.begin() ; j!=trueCover._map.end() ; ++j) {
        auto i = _map.find(j->first);
        if (i == _map.end()) {
            fn += j->second.size();
        }
    }
    return CoverMetrics(tp, fp, tn, fn);
}

template<class T> std::map<std::string, CoverMetrics>
Cover<T>::documentMetrics(Cover<T> const& trueCover) const
throw(std::runtime_error) {
    std::map<std::string, CoverMetrics> m;
    for (auto i=_map.begin() ; i!=_map.end() ; ++i) {
        auto j = trueCover._map.find(i->first);
        // if second cover is not found, assume it is empty
        if (j == trueCover._map.end()) {
            m[i->first] = CoverMetrics(0, i->second.size(), 0, 0);
        } else {
            m[i->first] = i->second.metrics(j->second);
        }
    }
    // stuff that is in second cover but not in first are false negatives
    for (auto j=trueCover._map.begin() ; j!=trueCover._map.end() ; ++j) {
        auto i = _map.find(j->first);
        if (i == _map.end()) {
            m[j->first] = CoverMetrics(0, 0, 0, j->second.size());
        }
    }
    return m;
}

template<class T> bool Cover<T>::operator==(Cover<T> const& other) const {
    if (_map.size() != other._map.size()) {
        return false;
    }
    for (auto i=_map.begin() ; i!=_map.end() ; ++i) {
        auto j = other._map.find(i->first);
        if (j == other._map.end()) {
            return false;
        } else if (i->second != j->second) {
            return false;
        }
    }
    return true;
}

template<class T> bool Cover<T>::operator!=(Cover<T> const& other) const {
    return !(*this == other);
}

template<class T> Cover<T> const& Cover<T>::operator&=(Cover<T> const& other)
throw(std::runtime_error) {
    _maptype m;
    for (auto i=_map.begin() ; i!=_map.end() ; ++i) {
        auto j = other._map.find(i->first);
        if (j != other._map.end()) {
            if (i->second.docSize() != j->second.docSize()) {
                throw std::runtime_error(ERR_MISMATCHING_DOC_SIZES);
            }
            m.insert(m.end(), {i->first, i->second & j->second});
        }
    }
    _map = m;
    return *this;
}

template<class T> Cover<T> const& Cover<T>::operator|=(Cover<T> const& other)
throw(std::runtime_error) {
    for (auto i=_map.begin() ; i!=_map.end() ; ++i) {
        auto j = other._map.find(i->first);
        if (j != other._map.end()) {
            if (i->second.docSize() != j->second.docSize()) {
                throw std::runtime_error(ERR_MISMATCHING_DOC_SIZES);
            }
            i->second |= j->second;
        }
    }
    for (auto j=other._map.begin() ; j!=other._map.end() ; ++j) {
        // document exists in second, but not in first, just add it
        if (_map.find(j->first) == _map.end()) {
            _map[j->first] = j->second;
        }
    }
    //_map = m;
    return *this;
}

template<class T> Cover<T> const& Cover<T>::operator-=(Cover<T> const& other)
throw(std::runtime_error) {
    for (auto i=_map.begin() ; i!=_map.end() ; ++i) {
        auto j = other._map.find(i->first);
        if (j != other._map.end()) {
            if (i->second.docSize() != j->second.docSize()) {
                throw std::runtime_error(ERR_MISMATCHING_DOC_SIZES);
            }
            i->second -= j->second;
        }
    }
    return *this;
}

template<class T> Cover<T> const& Cover<T>::operator^=(Cover<T> const& other)
throw(std::runtime_error) {
    for (auto i=_map.begin() ; i!=_map.end() ; ++i) {
        auto j = other._map.find(i->first);
        if (j != other._map.end()) {
            if (i->second.docSize() != j->second.docSize()) {
                throw std::runtime_error(ERR_MISMATCHING_DOC_SIZES);
            }
            i->second ^= j->second;
        }
    }
    for (auto j=other._map.begin() ; j!=other._map.end() ; ++j) {
        auto i = _map.find(j->first);
        if (i == _map.end()) {
            _map[j->first] = j->second;
        }
    }
    return *this;
}

template<class T> Cover<T> Cover<T>::operator&(Cover<T> const& other) {
    Cover<T> c(*this);
    c &= other;
    return c;
}

template<class T> Cover<T> Cover<T>::operator|(Cover<T> const& other) {
    Cover<T> c(*this);
    c |= other;
    return c;
}

template<class T> Cover<T> Cover<T>::operator-(Cover<T> const& other) {
    Cover<T> c(*this);
    c -= other;
    return c;
}

template<class T> Cover<T> Cover<T>::operator^(Cover<T> const& other) {
    Cover<T> c(*this);
    c ^= other;
    return c;
}

// explicitly define some convenience functions to convert cover to basic
// mappings.

/// Convert map of OrderedDocCovers to StringMapLongVector.
StringMapLongVector asLvFromOc(std::map<std::string, OrderedDocCover> const& m);
/// Convert map of BitsetDocCovers to StringMapLongVector.
StringMapLongVector asLvFromBc(std::map<std::string, BitsetDocCover> const& m);
/// Convert map of OrderedDocCovers to StringMapBoolVector.
StringMapBoolVector asBvFromOc(std::map<std::string, OrderedDocCover> const& m);
/// Convert map of BitsetDocCovers to StringMapBoolVector.
StringMapBoolVector asBvFromBc(std::map<std::string, BitsetDocCover> const& m);
/// Convert map of OrderedDocCovers to map of their related document sizes.
StringMapLong asSizesFromOc(std::map<std::string, OrderedDocCover> const& m);
/// Convert map of BitsetDocCovers to map of their related document sizes.
StringMapLong asSizesFromBc(std::map<std::string, BitsetDocCover> const& m);

// explicitly define some convenience functions to convert basic mappings
// to covers.
std::map<std::string, OrderedDocCover> asOc(StringMapLongVector const& m,
        StringMapLong const& sz)
throw (std::runtime_error);
std::map<std::string, OrderedDocCover> asOc(StringMapBoolVector const& m);
std::map<std::string, BitsetDocCover> asBc(StringMapLongVector const& m,
        StringMapLong const& sz)
throw (std::runtime_error);
std::map<std::string, BitsetDocCover> asBc(StringMapBoolVector const& m);

/// Convert an OrderedCover to BitsetCover.
Cover<BitsetDocCover> asBitsetCover(Cover<OrderedDocCover> const& c);
/// Convert a BitsetCover to OrderedCover.
Cover<OrderedDocCover> asOrderedCover(Cover<BitsetDocCover> const& c);

/// Given a vector of covers, true cover, return a vector of
/// max length `limit`, that contains the cover indices in order, which
/// maxizes the recall, if covers are unioned. The order is determined in a
/// greedy fashion. First, the cover with maximal recall is selected, then
/// the cover, which adds most to the metric and so on. Usually this function
/// is reasonable only for recall.
std::vector<long>
cumulativeOrdering(std::vector<OrderedCover> const& covers,
                   OrderedCover const& trueCover,
                   size_t const limit);

} // end pfe namespace
#endif
