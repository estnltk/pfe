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

#ifndef _PFE_COVERMETRICS_HPP_
#define _PFE_COVERMETRICS_HPP_

#include <PfeLib.hpp>

namespace pfe {

/// Class containing cover specific statistical metrics.
class CoverMetrics {
    long _tp, _fp, _tn, _fn;
public:
    CoverMetrics() : _tp(0), _fp(0), _tn(0), _fn(0) { }
    CoverMetrics(long tp, long fp, long tn, long fn)
        : _tp(tp), _fp(fp), _tn(tn), _fn(fn) {
    }
    // getter / setter for tp
    long tp() const {
        return _tp;
    }
    void tp(long tp) {
        _tp = tp;
    }
    // getter / setter for fp
    long fp() const {
        return _fp;
    }
    void fp(long fp) {
        _fp = fp;
    }
    // getter / setter for tn
    long tn() const {
        return _tn;
    }
    void tn(long tn) {
        _tn = tn;
    }
    // getter / setter for fn
    long fn() const {
        return _fn;
    }
    void fn(long fn) {
        _fn = fn;
    }
    /// Compute precision.
    double precision() const;
    /// Compute recall.
    double recall() const;
    /// Compute f1-score (harmonic mean of precision and recall).
    double f1score() const;
    /// Compute accuracy.
    double accuracy() const;
    /// Compute false positive rate.
    double fprate() const;
    /// Specificity (1-fprate)
    double specificity() const;
    /// Compute false negative rate.
    double fnrate() const;
    /// Compute Matthews correlation coefficient.
    double matthews() const;
    /// Compute support
    double support() const;
    /// Return a map containing all metrics.
    StringMapDouble all() const;
};

} // namespace pfe

#endif // _PFE_COVERMETRICS_HPP_
