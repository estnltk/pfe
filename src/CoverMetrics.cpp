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
#include "CoverMetrics.hpp"

namespace pfe {

double CoverMetrics::precision() const {
    if (_tp + _fp == 0) {
        return std::sqrt(-1); // return NaN
    }
    return _tp/static_cast<double>(_tp + _fp);
}

double CoverMetrics::recall() const {
    if (_tp + _fn == 0) {
        return std::sqrt(-1); // return NaN
    }
    return _tp/static_cast<double>(_tp + _fn);
}

double CoverMetrics::f1score() const {
    double p = precision();
    double r = recall();
    if (p + r < std::numeric_limits<double>::epsilon()) {
        return std::sqrt(-1); // return NaN
    }
    return 2*p*r/(p + r);
}

double CoverMetrics::accuracy() const {
    if (_tp + _fp + _tn + _fn == 0) {
        return std::sqrt(-1); // return NaN
    }
    return (_tp + _tn)/static_cast<double>(_tp + _fp + _tn + _fn);
}

double CoverMetrics::fprate() const {
    if (_fp + _tn == 0) {
        return std::sqrt(-1); // return NaN
    }
    return _fp/static_cast<double>(_fp + _tn);
}

double CoverMetrics::specificity() const {
    return 1.0 - fprate();
}

double CoverMetrics::fnrate() const {
    if (_tp + _fn == 0) {
        return std::sqrt(-1); // return NaN
    }
    return _fn/static_cast<double>(_tp + _fn);
}

double CoverMetrics::matthews() const {
    long numerator   = _tp*_tn - _fp*_fn;
    long denominator = (_tp + _fp)*(_tp + _fn)*(_tn + _fp)*(_tn + _fn);
    if (denominator == 0) {
        return std::sqrt(-1); // return NaN
    }
    return numerator / std::sqrt(static_cast<double>(denominator));
}
double CoverMetrics::support() const {
    return _tp + _fp;
}

/// Return a map containing all metrics.
StringMapDouble CoverMetrics::all() const {
    StringMapDouble m;
    m["tp"] = tp();
    m["fp"] = fp();
    m["tn"] = tn();
    m["fn"] = fn();
    m["precision"]   = precision();
    m["recall"]      = recall();
    m["f1score"]     = f1score();
    m["accuracy"]    = accuracy();
    m["fprate"]      = fprate();
    m["specificity"] = specificity();
    m["fnrate"]      = fnrate();
    m["matthews"]    = matthews();
    return m;
}

} // namespace pfe
