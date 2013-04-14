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
#include <Cover.hpp>

#include <boost/unordered_set.hpp>

namespace pfe {

StringMapLongVector
asLvFromOc(std::map<std::string, OrderedDocCover> const& m) {
    StringMapLongVector _m;
    for (auto i=m.begin() ; i!=m.end() ; ++i) {
        _m.insert(_m.end(), {i->first, i->second.indices()});
    }
    return _m;
}

StringMapLongVector asLvFromBc(std::map<std::string, BitsetDocCover> const& m) {
    StringMapLongVector _m;
    for (auto i=m.begin() ; i!=m.end() ; ++i) {
        _m.insert(_m.end(), {i->first, OrderedDocCover(i->second).indices()});
    }
    return _m;
}

StringMapBoolVector
asBvFromOc(std::map<std::string, OrderedDocCover> const& m) {
    StringMapBoolVector _m;
    for (auto i=m.begin() ; i!=m.end() ; ++i) {
        _m.insert(_m.end(), {i->first, BitsetDocCover(i->second).bits()});
    }
    return _m;
}

StringMapBoolVector asBvFromBc(std::map<std::string, BitsetDocCover> const& m) {
    StringMapBoolVector _m;
    for (auto i=m.begin() ; i!=m.end() ; ++i) {
        _m.insert(_m.end(), {i->first, i->second.bits()});
    }
    return _m;
}


StringMapLong asSizesFromOc(std::map<std::string, OrderedDocCover> const& m) {
    StringMapLong _m;
    for (auto i=m.begin() ; i!=m.end() ; ++i) {
        _m.insert(_m.end(), {i->first, i->second.docSize()});
    }
    return _m;
}

StringMapLong asSizesFromBc(std::map<std::string, BitsetDocCover> const& m) {
    StringMapLong _m;
    for (auto i=m.begin() ; i!=m.end() ; ++i) {
        _m.insert(_m.end(), {i->first, i->second.docSize()});
    }
    return _m;
}

std::map<std::string, OrderedDocCover> asOc(StringMapLongVector const& m,
        StringMapLong const& sz)
throw(std::runtime_error) {
    std::map<std::string, OrderedDocCover> _m;
    for (auto i=m.begin() ; i!=m.end() ; ++i) {
        auto j = sz.find(i->first);
        if (j == sz.end()) {
            throw std::runtime_error(ERR_SIZE_NOT_DEFINED);
        }
        _m.insert(_m.end(), {i->first, OrderedDocCover(j->second, i->second)});
    }
    return _m;
}

std::map<std::string, OrderedDocCover> asOc(StringMapBoolVector const& m) {
    std::map<std::string, OrderedDocCover> _m;
    for (auto i=m.begin() ; i!=m.end() ; ++i) {
        _m.insert(_m.end(),
        {i->first, OrderedDocCover(BitsetDocCover(i->second))});
    }
    return _m;
}

std::map<std::string, BitsetDocCover> asBc(StringMapLongVector const& m,
        StringMapLong const& sz)
throw (std::runtime_error) {
    std::map<std::string, BitsetDocCover> _m;
    for (auto i=m.begin() ; i!=m.end() ; ++i) {
        auto j = sz.find(i->first);
        if (j == sz.end()) {
            throw std::runtime_error(ERR_SIZE_NOT_DEFINED);
        }
        _m.insert(_m.end(),
        {i->first, BitsetDocCover(OrderedDocCover(j->second, i->second))});
    }
    return _m;
}

std::map<std::string, BitsetDocCover> asBc(StringMapBoolVector const& m) {
    std::map<std::string, BitsetDocCover> _m;
    for (auto i=m.begin() ; i!=m.end() ; ++i) {
        _m.insert(_m.end(), {i->first, BitsetDocCover(i->second)});
    }
    return _m;
}

Cover<BitsetDocCover> asBitsetCover(Cover<OrderedDocCover> const& c) {
    Cover<BitsetDocCover> bc;
    auto names = c.names();
    for (auto i=names.begin(); i!=names.end() ; ++i) {
        BitsetDocCover bdc(c.docCover(*i));
        bc.addDocCover(*i, bdc);
    }
    return bc;
}

Cover<OrderedDocCover> asOrderedCover(Cover<BitsetDocCover> const& c) {
    Cover<OrderedDocCover> oc;
    auto names = c.names();
    for (auto i=names.begin(); i!=names.end() ; ++i) {
        BitsetDocCover odc(c.docCover(*i));
        oc.addDocCover(*i, odc);
    }
    return oc;
}

std::vector<long>
cumulativeOrdering(std::vector<OrderedCover> const& covers,
                   OrderedCover const& trueCover,
                   size_t const limit)
{
    OrderedCover _cumulative;
    OrderedCover _candidate;
    std::vector<long> _result;
    boost::unordered_set<size_t> _used;
    for (size_t idx=0 ; idx<limit && _used.size() < covers.size() ; ++idx) {
        double best_value = std::numeric_limits<double>::min();
        size_t best_idx = 0;
        for (size_t covIdx=0 ; covIdx < covers.size() ; ++covIdx) {
            // if have already considered the cover, do not waste time
            // testing it again
            auto i = _used.find(covIdx);
            if (i != _used.end()) {
                continue;
            }
            // check, how much is the recall, when combined with the
            // cumulative cover so far.
            _candidate = _cumulative | covers[covIdx];
            double value = _candidate.metrics(trueCover).recall();
            if (value > best_value) {
                best_value = value;
                best_idx = covIdx;
            }
        }
        // add the best cover
        _used.insert(best_idx);
        _cumulative |= covers[best_idx];
        _result.push_back(best_idx);
    }
    return _result;
}

} //namespace pfe
