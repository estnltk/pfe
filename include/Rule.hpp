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
#ifndef _PFE_RULE_HPP_
#define _PFE_RULE_HPP_

#include <PfeLib.hpp>
#include <DocCover.hpp>
#include <Cover.hpp>
#include <Corpus.hpp>

namespace pfe {

typedef std::pair<long, std::string> Rule;
typedef std::vector<Rule> Conjunction;
typedef std::vector<Conjunction> Disjunction;

typedef std::map<Rule, OrderedDocCover> RuleOrderedDocCover;
typedef std::map<Rule, OrderedCover> RuleOrderedCover;

/// Extract Rules from the document with their covers.
/// @param document: The document the rules will be extracted from.
/// @param radius: Context radius to use for creating the rules.
std::map<Rule, OrderedDocCover>
docBasicRuleCovers(Document const& document, long const radius=2);

/// Extract rules from the corpus with their covers.
/// @param corpus: The corpus of documents the rules will be extracted from.
/// @param radius: Context radius to use for creating the rules.
std::map<Rule, OrderedCover>
basicRuleCovers(Corpus const& corpus, long const radius=2);

/// Extract full specific conjunctions from a single document.
std::set<Conjunction>
docFullConjunctions(Document const& document, long const radius);

/// Extract full specific conjunctions from corpus.
std::vector<Conjunction>
fullConjunctions(Corpus const& corpus, long const radius=2);

/// Count the number of different basic rules in Document.
std::map<Rule, long>
docRuleCount(Document const& document, long const radius=2);

/// Count the number of different basic rules in Corpus.
std::map<Rule, long>
corpusRuleCount(Corpus const& corpus, long const radius=2);

/// Create conjunction pairs
std::vector<Conjunction> conjunctionPairs(std::vector<Conjunction> const& A,
                                          std::vector<Conjunction> const& B);

/// Unique conjunctions
std::vector<Conjunction> uniqueConjunctions(std::vector<Conjunction> const& A);

/// Compute the cover of a conjunction.
OrderedCover conjunctionCover(Conjunction const& c,
                            std::map<Rule, OrderedCover> const& basicCovers);


/// Reorder a list of conjunctions according to recall.
std::vector<Conjunction>
reorderRecall(std::vector<Conjunction> const& conjunctions,
              std::map<Rule, OrderedCover> const& basicCovers,
              OrderedCover const& trueCover);

} //namespace pfe

#endif
