%module session
%feature("autodoc", "0");

%{
#include "../include/datatypes.h"
%}

%include "stl.i"
%include "../include/datatypes.h"  // Include it again for SWIG to process

%template(_result_list) std::vector<Result>;
%template(_string_list) std::vector< std::string >;

%feature("kwargs") Session::Session;

%exception {
    try {
        $action
    } catch (const std::runtime_error& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        SWIG_fail;
    }
};

// Tell SWIG how to print our datatype Result in python
%extend Result {
    std::string to_string() {
        return self->to_string();
    }
}

%pythoncode {
    class Result:
        def __str__(self):
            return self.to_string()
}

%{
#include "session.h"
%}

// Now list ANSI C/C++ declarations
%include "../include/session.h"