%module session
%feature("autodoc", "0");

%include "stl.i"

%feature("kwargs") Session::Session;

// Tell SWIG how to handle our special return type from C++
%template(_string_list) std::vector<std::string>;

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