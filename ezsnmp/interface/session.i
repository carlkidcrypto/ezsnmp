%module session
%feature("autodoc", "0");

%include "stl.i"
%include "datatypes.i"

%feature("kwargs") Session::Session;
%feature("python:annotations", "c");

// Tell SWIG how to handle our special return type(s) from C++
%template(_string_list) std::vector<std::string>;
%template(_result_list) std::vector<Result>;

// Tell SWIG we want C++ errors converted to proper high-level language errors
%exception {
    try {
        $action
    } catch (const std::runtime_error& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        SWIG_fail;
    }
};

%{
#include "session.h"
%}

// Now list ANSI C/C++ declarations
%include "../include/session.h"