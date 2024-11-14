%module netsnmp
%include "argcargv.i"
%include "stl.i"

// Tell SWIG we want C++ errors converted to proper high-level language errors
%exception {
    try {
        $action
    } catch (const std::runtime_error& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        SWIG_fail;
    } catch (const std::invalid_argument& e) {
        PyErr_SetString(PyExc_ValueError, e.what());
        SWIG_fail;
    }
};

%{
#include "snmpgetnext.h"
%}

// Now list ANSI C/C++ declarations
std::vector<Result> snmpgetnext(std::vector<std::string> const &args);