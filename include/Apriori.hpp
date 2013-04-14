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
#ifndef _PFE_APRIORI_HPP_
#define _PFE_APRIORI_HPP_

#include <PfeLib.hpp>
#include <Cover.hpp>
#include <CoverMetrics.hpp>
#include <Rule.hpp>

namespace pfe {

/// Mine high recall frequent rules.
std::vector<Conjunction>
hrApriori(std::vector<Conjunction> const& initial,
        std::map<Rule, OrderedCover> const& basicCovers,
        OrderedCover const& trueCover,
        double treshold,
        long limit=2,
        long numThreads=2)
throw(std::runtime_error);

/// Mine high precision frequent rules.
std::vector<Conjunction>
hpApriori(std::vector<Conjunction> const& initial,
        std::map<Rule, OrderedCover> const& basicCovers,
        OrderedCover const& trueCover,
        double treshold,
        long limit=2,
        long numThreads=2)
throw(std::runtime_error);

} //namespace pfe

#endif
