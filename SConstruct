# Pattern based fact extraction library.
# build file

# use `scons lib` to build standard C++ library
# use `scons python` to build python wrapper
# use `scons R' to build R wrapper

import SCons.Script
import os, sys
import shutil
import string

# specify include path and source files to be used
CPPPATH = 'include:/usr/include/python2.7:/usr/include/R/'

PFE_SRC = ['src/Cover.cpp',
           'src/CoverMetrics.cpp',
           'src/DocCover.cpp',
           'src/Corpus.cpp',
           'src/Rule.cpp',
           'src/Apriori.cpp']

# C++ flags
CXXFLAGS = '-std=c++0x -O3 -Wall -Wfatal-errors'

LIBS = ['boost_thread']

# set up SwigScanner
SWIGScanner = SCons.Scanner.ClassicCPP(
    "SWIGScan",
    ".i",
    "CPPPATH",
    '^[ \t]*[%,#][ \t]*(?:include|import)[ \t]*(<|")([^>"]+)(>|")'
)

# method for wrapping exceptions in custom code
def wrap_exception(funcall):
    try:
        return funcall()
    except Exception, e:
        sys.stderr.write(str(e) + '\n')

# set up environment for standard library
libenv = Environment(
    ENV = os.environ,
    CPPPATH=CPPPATH,
    CXXFLAGS=CXXFLAGS,
    LIBS=LIBS,
    SHLIBPREFIX='')

# python wrapper environment
pyenv = Environment(
    ENV = os.environ,
    CPPPATH=CPPPATH,
    CXXFLAGS=CXXFLAGS,
    SWIGFLAGS='-c++ -python',
    LIBS=LIBS,
    SHLIBPREFIX='')


# R wrapper environment
Renv = Environment(
    ENV = os.environ,
    CPPPATH=CPPPATH,
    CXXFLAGS=CXXFLAGS,
    SWIGFLAGS='-c++ -r',
    LIBS=LIBS,
    SHLIBPREFIX='')

def fix_r_interface_file():
    code = open(os.path.join('swig', 'rpfe.i'), 'rb').read()
    code = string.replace(code, '%module pypfe', '%module rpfe')
    open(os.path.join('swig', 'rpfe.i'), 'wb').write(code)

# add SWIG scanner
pyenv.Prepend(SCANNERS=[SWIGScanner])
#Renv.Prepend(SCANNERS=[SWIGScanner])

# prepare targets
lib   = os.path.join('lib', libenv['LIBPREFIX']  + 'pfe'   + libenv['LIBSUFFIX'])
pylib = os.path.join('lib', pyenv['SHLIBPREFIX'] + '_pypfe' + pyenv['SHLIBSUFFIX'])
#rlib  = os.path.join('lib', Renv['SHLIBPREFIX']  + 'rpfe'  + Renv['SHLIBSUFFIX'])

# name aliases to targets
libenv.Alias('lib', lib)
pyenv.Alias('python', pylib)
#Renv.Alias('R', rlib)

# build the C++ library
libenv.Library(lib, PFE_SRC)

# build Python binding
pyenv.SharedLibrary(pylib, PFE_SRC + ['swig/pfe.i'])
wrap_exception(lambda: shutil.copyfile(os.path.join('swig', 'pypfe.py'), os.path.join('pypfe','pfe.py')))
print "NOTE: run test/pfelibtest.py to test the Python version of the library"

# build R binding
#wrap_exception(lambda: shutil.copyfile(os.path.join('swig', 'pfe.i'), os.path.join('swig', 'rpfe.i')))
#wrap_exception(fix_r_interface_file)
#Renv.SharedLibrary(rlib, PFE_SRC + ['swig/rpfe.i'])
#wrap_exception(lambda: shutil.copyfile(os.path.join('swig', 'rpfe.R'), os.path.join('lib','pfe.R')))

