%module session
%feature("autodoc", "0");

%{
#include "../include/datatypes.h"
%}

%include "stl.i"
%include "../include/datatypes.h"  // Include it again for SWIG to process

%template(_result_list) std::vector<Result>;

%feature("kwargs") Session::Session;

%exception {
    try {
        $action
    } catch (const std::runtime_error& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        SWIG_fail;
    }
};

%extend Result {
    std::string __str__() {
        return self->to_string();
    }
};

%{
#include "session.h"
%}

// Now list ANSI C/C++ declarations
%include "../include/session.h"