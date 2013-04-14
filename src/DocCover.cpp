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
#include "DocCover.hpp"

#include <set>
#include <algorithm>

namespace pfe {

////////////////////////////////////////////////////////////////////////////////
// OrderedDocCover
////////////////////////////////////////////////////////////////////////////////

OrderedDocCover::OrderedDocCover(BitsetDocCover const& other)
    : DocCover(other.docSize()) {
    _indices.reserve(other.size());
    for (auto i=0 ; i<other.docSize() ; ++i) {
        if (other._bits[i]) {
            _indices.push_back(i);
        }
    }
    assert (_indices.size() == other._bits.count());
}

void OrderedDocCover::initializeIndices() throw(std::runtime_error) {
    // first check that all elements are contained in the document
    for (auto i=_indices.begin() ; i != _indices.end() ; ++i) {
        if (*i >= docSize() || *i < 0) {
            throw std::runtime_error(ERR_INVALID_COVER_ELEMENT);
        }
    }
    std::set<long> s(_indices.begin(), _indices.end());
    _indices.clear();
    _indices.insert(_indices.begin(), s.begin(), s.end());
}

CoverMetrics OrderedDocCover::metrics(OrderedDocCover const& trueCover) const
throw(std::runtime_error) {
    if (docSize() != trueCover.docSize()) {
        throw std::runtime_error(ERR_MISMATCHING_DOC_SIZES);
    }
    long tp = (*this & trueCover).size();
    long fp = (*this - trueCover).size();
    long fn = (trueCover - *this).size();
    long tn = docSize() - (*this | trueCover).size();
    return CoverMetrics(tp, fp, tn, fn);
}

OrderedDocCover const&
OrderedDocCover::operator&=(OrderedDocCover const& other) {
    LongVector indices;
    std::set_intersection(_indices.begin(),
                          _indices.end(),
                          other._indices.begin(),
                          other._indices.end(),
                          std::back_inserter(indices));
    _indices = indices;
    return *this;
}

OrderedDocCover const&
OrderedDocCover::operator|=(OrderedDocCover const& other) {
    LongVector indices;
    std::set_union(_indices.begin(),
                   _indices.end(),
                   other._indices.begin(),
                   other._indices.end(),
                   std::back_inserter(indices));
    _indices = indices;
    return *this;
}

OrderedDocCover const&
OrderedDocCover::operator-=(OrderedDocCover const& other) {
    LongVector indices;
    std::set_difference(_indices.begin(),
                        _indices.end(),
                        other._indices.begin(),
                        other._indices.end(),
                        std::back_inserter(indices));
    _indices = indices;
    return *this;
}
OrderedDocCover const&
OrderedDocCover::operator^=(OrderedDocCover const& other) {
    LongVector indices;
    std::set_symmetric_difference(_indices.begin(),
                                  _indices.end(),
                                  other._indices.begin(),
                                  other._indices.end(),
                                  std::back_inserter(indices));
    _indices = indices;
    return *this;
}

OrderedDocCover OrderedDocCover::operator&(OrderedDocCover const& other) const {
    OrderedDocCover c(*this);
    c &= other;
    return c;
}

OrderedDocCover OrderedDocCover::operator|(OrderedDocCover const& other) const {
    OrderedDocCover c(*this);
    c |= other;
    return c;
}

OrderedDocCover OrderedDocCover::operator-(OrderedDocCover const& other) const {
    OrderedDocCover c(*this);
    c -= other;
    return c;
}

OrderedDocCover OrderedDocCover::operator^(OrderedDocCover const& other) const {
    OrderedDocCover c(*this);
    c ^= other;
    return c;
}

bool OrderedDocCover::operator==(OrderedDocCover const& other) const {
    if (this == &other) { // same object
        return true;
    }
    return docSize() == other.docSize() && _indices == other._indices;
}

////////////////////////////////////////////////////////////////////////////////
// BitsetDocCover
////////////////////////////////////////////////////////////////////////////////

BitsetDocCover::BitsetDocCover(BoolVector const& bits) : DocCover(bits.size()) {
    _bits.resize(bits.size());
    for (size_t i=0 ; i<bits.size() ; ++i) {
        _bits[i] = bits[i];
    }
}

BitsetDocCover::BitsetDocCover(OrderedDocCover const& other)
    : DocCover(other.docSize()) {
    _bits.resize(other.docSize());
    for (auto i=other._indices.begin() ; i!=other._indices.end() ; ++i) {
        _bits[*i] = true;
    }
    assert (_bits.count() == other._indices.size());
}

BoolVector BitsetDocCover::bits() const {
    BoolVector v(docSize());
    for (auto i=0 ; i<docSize() ; ++i) {
        v[i] = _bits[i];
    }
    return v;
}

CoverMetrics BitsetDocCover::metrics(BitsetDocCover const& trueCover) const
throw(std::runtime_error) {
    if (docSize() != trueCover.docSize()) {
        throw std::runtime_error(ERR_MISMATCHING_DOC_SIZES);
    }
    long tp = (*this & trueCover).size();
    long fp = (*this - trueCover).size();
    long fn = (trueCover - *this).size();
    long tn = docSize() - (*this | trueCover).size();
    return CoverMetrics(tp, fp, tn, fn);
}

bool BitsetDocCover::operator==(BitsetDocCover const& other) const {
    if (this == &other) { // same object
        return true;
    }
    return _bits == other._bits;
}

BitsetDocCover const& BitsetDocCover::operator&=(BitsetDocCover const& other) {
    _bits &= other._bits;
    return *this;
}

BitsetDocCover const& BitsetDocCover::operator|=(BitsetDocCover const& other) {
    _bits |= other._bits;
    return *this;
}

BitsetDocCover const& BitsetDocCover::operator-=(BitsetDocCover const& other) {
    _bits -= other._bits;
    return *this;
}

BitsetDocCover const& BitsetDocCover::operator^=(BitsetDocCover const& other) {
    _bits ^= other._bits;
    return *this;
}

BitsetDocCover BitsetDocCover::operator&(BitsetDocCover const& other) const {
    BitsetDocCover c(*this);
    c &= other;
    return c;
}

BitsetDocCover BitsetDocCover::operator|(BitsetDocCover const& other) const {
    BitsetDocCover c(*this);
    c |= other;
    return c;
}

BitsetDocCover BitsetDocCover::operator-(BitsetDocCover const& other) const {
    BitsetDocCover c(*this);
    c -= other;
    return c;
}

BitsetDocCover BitsetDocCover::operator^(BitsetDocCover const& other) const {
    BitsetDocCover c(*this);
    c ^= other;
    return c;
}

} // namespace pfe
