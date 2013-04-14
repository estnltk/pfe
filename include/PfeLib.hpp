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

Code style of PFE C++ library:
    - indents are 4 spaces.
    - variable names are smallCamelCase.
    - class names are CamelCase.
    - if, while, for have space between expression. Additionally, conditions
      are written without spaces.
        example: for (i=0 ; i<10 ; ++i) {
    - no single line if, else.
        example: if (a==True) do_sth(); // <- this is dangerous.
    - private class members are prefixed with _.
    - getters and setters have same name as private member.
        example:
            long _private;
            long private() const { return _private; }
            void private(long const newPrivate) { _private = newPrivate };
    - max line width is 80 characters.
    - avoid empty lines inside class headers, method definitions and functions.
      This way more code fits on screen. Add blank lines only if you feel
      that it improves readability or better, add some comments instead.
    - force const-correctness whenever possible.
    - use "MyClass const&" instead of "const MyClass&" and do same in other
      similar situations.
    - prefer /// for docstrings in class, method and function definitions.
    - prefer simple methods over complicated ones.
      KISS (keep it simple, Sydney!)
*/
#ifndef _PFE_PFE_LIB_HPP
#define _PFE_PFE_LIB_HPP

// include standard headers used everywhere
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <utility>
#include <iterator>
#include <exception>
#include <stdexcept>
#include <limits>
#include <map>
#include <set>
#include <cmath>

namespace pfe {

// define basic errors thrown by exceptions
#define ERR_DOCSIZE_LESS_0 "001: Document size less than 0"
#define ERR_INVALID_COVER_ELEMENT "002: Invalid cover element."
#define ERR_MISMATCHING_DOC_SIZES "003: Document sizes differ."
#define ERR_DOC_NOT_FOUNT "004: Document not found in cover."
#define ERR_SIZE_NOT_DEFINED "005: Size not defined for document."
#define ERR_DOC_WITH_NAME_EXIST "006: Document with given name already present!"
#define ERR_COULD_NOT_READ_FILE "007: Could not read file "
#define ERR_COULD_NOT_WRITE_FILE "008: Could not write file "
#define ERR_TRESHOLD_INSANE "009: Your treshold is too low or too high to obtain any meaningul results for given data."
#define ERR_DOCUMENT_NOT_FOUND "010: Document not found"

typedef std::vector<long> LongVector;
typedef std::vector<std::string> StringVector;
typedef std::vector<bool> BoolVector;

typedef std::map<std::string, long> StringMapLong;
typedef std::map<std::string, double> StringMapDouble;
typedef std::map<std::string, LongVector> StringMapLongVector;
typedef std::map<std::string, BoolVector> StringMapBoolVector;

#define PFE_VERSION_MAJOR   0
#define PFE_VERSION_MINOR   3

}

#endif
