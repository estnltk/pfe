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

#include <Apriori.hpp>

#include <set>

#include <boost/thread.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/unordered_set.hpp>
#include <boost/random/mersenne_twister.hpp>
#include <boost/random/discrete_distribution.hpp>

namespace pfe {

////////////////////////////////////////////////////////////////////////////////
// high recall
////////////////////////////////////////////////////////////////////////////////
void hrFrequentThread(
    long start,
    long stop,
    std::vector<Conjunction> const& conjunctions,
    std::map<Rule, OrderedCover> const& basicCovers,
    OrderedCover const& trueCover,
    double const treshold,
    std::vector<Conjunction>& result,
    boost::mutex& mutex
    )
{
    std::vector<Conjunction> _result;
    _result.reserve(stop-start);
    auto start_i = conjunctions.begin();
    auto stop_i  = conjunctions.begin();
    std::advance(start_i, start);
    std::advance(stop_i, stop);
    long counter = 0;
    for (auto i=start_i ; i!=stop_i ; ++i) {
        OrderedCover _ordc(conjunctionCover(*i, basicCovers));
        if (_ordc.metrics(trueCover).recall() >= treshold) {
            _result.push_back(*i);
            counter += 1;
        }
        // try copying intermediate results
        if (counter % 256 == 0) {
            if (mutex.try_lock()) {
                std::copy(_result.begin(), _result.end(),
                          std::back_inserter(result));
                mutex.unlock();
                _result.clear();
            }
        }
    }
    // copy to master _result vector
    mutex.lock();
    std::copy(_result.begin(), _result.end(), std::back_inserter(result));
    mutex.unlock();
}

std::vector<Conjunction> hrFrequent(
    std::vector<Conjunction> const& conjunctions,
    std::map<Rule, OrderedCover> const& basicCovers,
     OrderedCover const& trueCover,
     double const treshold,
     long const n_threads) {
    std::vector<Conjunction> _result; _result.reserve(conjunctions.size());
    double interval = static_cast<double>(conjunctions.size()) / n_threads;
    interval = std::max(interval, 1.0);

    boost::thread_group threads;
    boost::mutex mutex;

    for (double start=0 ; start<conjunctions.size() ; start+=interval) {
        long lstart = static_cast<long>(start);
        long lend   = static_cast<long>(start+interval);
        fprintf(stderr, "Thread will handle %lu to %lu\n", lstart, lend);
        threads.add_thread(new boost::thread(hrFrequentThread,
                                             lstart,
                                             lend,
                                             boost::ref(conjunctions),
                                             boost::ref(basicCovers),
                                             boost::ref(trueCover),
                                             treshold,
                                             boost::ref(_result),
                                             boost::ref(mutex)));
    }
    threads.join_all();

    return _result;
}

std::vector<Conjunction> hrCandidates(
    std::vector<Conjunction> const& conjunctions)
{
    boost::unordered_set<Conjunction> _present;
    std::set<Rule> _running;
    Conjunction _conjunction;

    for (auto i=conjunctions.begin() ; i!=conjunctions.end() ; ++i) {
        for (auto j=i+1 ; j!=conjunctions.end() ; ++j) {
            if (*i == *j) {
                continue;
            }
            // do the conjunction
            _running.clear();
            _running.insert(i->begin(), i->end());
            _running.insert(j->begin(), j->end());
            // create a conjunction, where individual components are sorted
            _conjunction.clear();
            _conjunction.insert(_conjunction.begin(),
                                _running.begin(), _running.end());
            // if it does not equal to none of its parents, add it
            if (_conjunction != *i && _conjunction != *j) {
                _present.insert(_conjunction);
            }
        }
    }
    std::vector<Conjunction> _result(_present.begin(), _present.end());
    return _result;
}

std::vector<Conjunction>
hrApriori(std::vector<Conjunction> const& initial,
        std::map<Rule, OrderedCover> const& basicCovers,
        OrderedCover const& trueCover,
        double treshold,
        long limit,
        long numThreads)
throw(std::runtime_error) {
    size_t N = trueCover.metrics(trueCover).support();
    // treshold is smaller than minimal single occurrence, everything that
    // exists, will be frequent.
    if (treshold <= 1.0 / N) {
        throw std::runtime_error(ERR_TRESHOLD_INSANE);
    }

    std::vector<Conjunction> _candidates = initial;
    std::vector<Conjunction> _frequent;
    std::vector<Conjunction> _result;
    fprintf(stderr, "Starting with %lu initial candidates\n", initial.size());

    for (long iter=1 ; _candidates.size() > 0 ; ++iter) {
        _frequent = hrFrequent(_candidates, basicCovers, trueCover, treshold,
                                                                    numThreads);
        fprintf(stderr, "iter %lu: %lu/%lu candidates are frequent\n",
                iter, _frequent.size(), _candidates.size());
        std::copy(_frequent.begin(), _frequent.end(),
                  std::back_inserter(_result));
        if (limit == iter) {
            break;
        }
        _candidates = uniqueConjunctions(hrCandidates(_frequent));
        fprintf(stderr, "obtained %lu new candidates\n", _candidates.size());
    }
    return uniqueConjunctions(_result);
}

////////////////////////////////////////////////////////////////////////////////
// high precision
////////////////////////////////////////////////////////////////////////////////

void hpFrequentThread(
    long start,
    long stop,
    std::vector<Conjunction> const& conjunctions,
    std::map<Rule, OrderedCover> const& basicCovers,
    OrderedCover const& trueCover,
    double const treshold,
    std::vector<Conjunction>& result,
    boost::mutex& mutex
    )
{
    std::vector<Conjunction> _result;
    _result.reserve(stop-start);
    auto start_i = conjunctions.begin();
    auto stop_i  = conjunctions.begin();
    std::advance(start_i, start);
    std::advance(stop_i, stop);
    long counter = 0;
    for (auto i=start_i ; i!=stop_i ; ++i) {
        OrderedCover _ordc(conjunctionCover(*i, basicCovers));
        //auto xxx = _ordc.metrics(trueCover);
        //printf("%d %d %d %d\n", xxx.tp(), xxx.fp(), xxx.tn(), xxx.fn());
        //printf("%lf\n", _ordc.metrics(trueCover).fprate());
        auto m = _ordc.metrics(trueCover);
        // also require precision to be good enough as fprate is
        // not reasonable metric anyway
        if (m.fprate() <= treshold && m.precision() > 0) {
            _result.push_back(*i);
            counter += 1;
        }
        // try copying intermediate results
        if (counter % 256 == 0) {
            if (mutex.try_lock()) {
                std::copy(_result.begin(), _result.end(),
                          std::back_inserter(result));
                mutex.unlock();
                _result.clear();
            }
        }
    }
    // copy to master _result vector
    mutex.lock();
    std::copy(_result.begin(), _result.end(), std::back_inserter(result));
    mutex.unlock();
}

std::vector<Conjunction> hpFrequent(
    std::vector<Conjunction> const& conjunctions,
    std::map<Rule, OrderedCover> const& basicCovers,
     OrderedCover const& trueCover,
     double const treshold,
     long const n_threads)
{
    std::vector<Conjunction> _result; _result.reserve(conjunctions.size());
    double interval = static_cast<double>(conjunctions.size()) / n_threads;
    interval = std::max(interval, 1.0);

    boost::thread_group threads;
    boost::mutex mutex;

    for (double start=0 ; start<conjunctions.size() ; start+=interval) {
        long lstart = static_cast<long>(start);
        long lend   = static_cast<long>(start+interval);
        fprintf(stderr, "Thread will handle %lu to %lu\n", lstart, lend);
        threads.add_thread(new boost::thread(hpFrequentThread,
                                             lstart,
                                             lend,
                                             boost::ref(conjunctions),
                                             boost::ref(basicCovers),
                                             boost::ref(trueCover),
                                             treshold,
                                             boost::ref(_result),
                                             boost::ref(mutex)));
    }
    threads.join_all();

    return _result;
}

std::vector<Conjunction> hpCandidates(
    std::vector<Conjunction> const& conjunctions,
    double const probability=0.1)
{
    boost::unordered_set<Conjunction> _present;
    std::set<Rule> _running;
    Conjunction _conjunction;
    // randomness
    boost::mt19937 gen;
    double probs[] = {probability, 1-probability};
    boost::random::discrete_distribution<> dist(probs);

    for (auto i=conjunctions.begin() ; i!=conjunctions.end() ; ++i) {
        //if (dist(gen) == 1) { // create a new pair with probability
        //    continue;
        //}
        for (auto j=i+1 ; j!=conjunctions.end() ; ++j) {
            if (*i == *j) {
                continue;
            }
            // do the conjunction intersection
            _running.clear();
            _running.insert(i->begin(), i->end());
            for (auto k=j->begin() ; k!=j->end() ; ++k) {
                _running.erase(*k);
            }
            if (_running.size() == 0) {
                continue; // do not allow rule which matches everything
            }
            // create a conjunction, where individual components are sorted
            _conjunction.clear();
            _conjunction.insert(_conjunction.begin(),
                                _running.begin(), _running.end());
            // if it does not equal to none of its parents, add it
            if (_conjunction != *i && _conjunction != *j) {
                _present.insert(_conjunction);
            }
        }
    }
    std::vector<Conjunction> _result(_present.begin(), _present.end());
    return _result;
}

std::vector<Conjunction>
hpApriori(std::vector<Conjunction> const& initial,
        std::map<Rule, OrderedCover> const& basicCovers,
        OrderedCover const& trueCover,
        double treshold,
        long limit,
        long numThreads)
throw(std::runtime_error) {
    size_t N = trueCover.metrics(trueCover).support();
    // treshold is smaller than minimal single occurrence, everything that
    // exists, will not be
    if (treshold <= 1.0 / N) {
        throw std::runtime_error(ERR_TRESHOLD_INSANE);
    }

    std::vector<Conjunction> _candidates = initial;
    std::vector<Conjunction> _frequent;
    std::vector<Conjunction> _result;
    fprintf(stderr, "Starting with %lu initial candidates\n", initial.size());

    for (long iter=1 ; _candidates.size() > 0 ; ++iter) {
        _frequent = hpFrequent(_candidates, basicCovers, trueCover, treshold,
                                                                    numThreads);
        fprintf(stderr, "iter %lu: %lu/%lu candidates are frequent\n",
                iter, _frequent.size(), _candidates.size());
        std::copy(_frequent.begin(), _frequent.end(),
                  std::back_inserter(_result));
        if (limit == iter) {
            break;
        }
        _candidates = uniqueConjunctions(hpCandidates(_frequent));
        fprintf(stderr, "obtained %lu new candidates\n", _candidates.size());
    }
    return uniqueConjunctions(_result);
}

} // namespace pfe
