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
#ifndef _PFE_DOCCOVER_HPP_
#define _PFE_DOCCOVER_HPP_

#include <PfeLib.hpp>
#include <CoverMetrics.hpp>

#include <boost/dynamic_bitset.hpp>

namespace pfe {

/// Base class for all document cover types.
class DocCover {
    /// Number of words in the document this cover is related to.
    long _docSize;
public:
    DocCover(long const docSize) throw (std::runtime_error): _docSize(docSize) {
        if (docSize < 0) {
            throw std::runtime_error(ERR_DOCSIZE_LESS_0);
        }
    };
    /// Get the document size the cover is related to.
    long docSize() const {
        return _docSize;
    };
};

class BitsetDocCover;

/// Document cover that represents the cover elements as a sorted list
/// of indices.
class OrderedDocCover : public DocCover {
    /// Internal vector of indices.
    LongVector _indices;
    /// Sort and remove duplicate elements from _indices.
    void initializeIndices() throw(std::runtime_error);
public:
    /// Initialize empty DocCover for zero-length document. This exists
    /// because we want to create maps to DocCovers, which require the type to
    /// be default constructable.
    OrderedDocCover() : DocCover(0) { }
    /// Initialize empty OrderedDocCover for a document of given size.
    OrderedDocCover(long const docSize) : DocCover(docSize) { }
    /// Copy constructor.
    OrderedDocCover(OrderedDocCover const& other)
        : DocCover(other.docSize()), _indices(other._indices) {
    }
    /// Initialize OrderedDocCover from given indices.
    OrderedDocCover(long const docSize, LongVector const& indices)
        : DocCover(docSize), _indices(indices) {
        initializeIndices();
    }
    /// Construct an OrderedDocCover from BitsetDocCover instance.
    OrderedDocCover(BitsetDocCover const& other);
    /// Return the indices of the OrderedDocCover instance.
    LongVector indices() const {
        return _indices;
    }
    /// Given a true cover (or other cover), compute the metrics object
    /// that can be used to get the precision, recall etc.
    CoverMetrics metrics(OrderedDocCover const& trueCover) const
    throw(std::runtime_error);
    /// Return the number of cover elements.
    long size() const {
        return _indices.size();
    }
    // overloaded operators.
    bool operator==(OrderedDocCover const& other) const;
    bool operator!=(OrderedDocCover const& other) const {
        return !(*this == other);
    }
    OrderedDocCover const& operator&=(OrderedDocCover const& other);
    OrderedDocCover const& operator|=(OrderedDocCover const& other);
    OrderedDocCover const& operator-=(OrderedDocCover const& other);
    OrderedDocCover const& operator^=(OrderedDocCover const& other);
    OrderedDocCover operator&(OrderedDocCover const& other) const;
    OrderedDocCover operator|(OrderedDocCover const& other) const;
    OrderedDocCover operator-(OrderedDocCover const& other) const;
    OrderedDocCover operator^(OrderedDocCover const& other) const;
    friend class BitsetDocCover;
};

/// BitsetDocCover representes the cover elements as set bits in a
/// bit vector of documents size.
class BitsetDocCover : public DocCover {
    /// Internal representation of the cover.
    boost::dynamic_bitset<> _bits;
public:
    /// Construct empty BitsetDocCover for zero-length document. This exists
    /// because we want to create maps to DocCovers, which require the type to
    /// be default constructable.
    BitsetDocCover() : DocCover(0) { }
    /// Construct empty BitsetDocCover for document of given size.
    BitsetDocCover(long const docSize) : DocCover(docSize) {
        _bits.resize(docSize);
    }
    /// Copy constructor.
    BitsetDocCover(BitsetDocCover const& other)
        : DocCover(other.docSize()), _bits(other._bits) {
    }
    /// Construct a BitsetDocCover form a vector of booleans.
    BitsetDocCover(BoolVector const& bits);
    /// Construct a BitsetDocCover from a OrderedDocCover.
    BitsetDocCover(OrderedDocCover const& other);
    /// Get the bits as a vector of booleans.
    BoolVector bits() const;
    /// Given a true cover (or other cover), compute the metrics object
    /// that can be used to get the precision, recall etc.
    CoverMetrics metrics(BitsetDocCover const& trueCover) const
    throw(std::runtime_error);
    /// Return the number of cover elements.
    /// Number of elements in the cover.
    long size() const {
        return _bits.count();
    }
    // overloaded operators.
    bool operator==(BitsetDocCover const& other) const;
    bool operator!=(BitsetDocCover const& other) const {
        return !(*this == other);
    }
    BitsetDocCover const& operator&=(BitsetDocCover const& other);
    BitsetDocCover const& operator|=(BitsetDocCover const& other);
    BitsetDocCover const& operator-=(BitsetDocCover const& other);
    BitsetDocCover const& operator^=(BitsetDocCover const& other);
    BitsetDocCover operator&(BitsetDocCover const& other) const;
    BitsetDocCover operator|(BitsetDocCover const& other) const;
    BitsetDocCover operator-(BitsetDocCover const& other) const;
    BitsetDocCover operator^(BitsetDocCover const& other) const;
    friend class OrderedDocCover;
};

} // namespace pfe

#endif // _PFE_DOCCOVER_HPP_
