%module netsnmp
%feature("autodoc", "0");

%{
#include "../include/datatypes.h"
%}

%include "stl.i"
%include "../include/datatypes.h"  // Include it again for SWIG to process

// Tell SWIG how to handle our special return type from c++
%template(_result_list) std::vector<Result>;

// Tell SWIG we want c++ errors converted to proper highlevel language errors
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
    std::string __str__() {
        return self->to_string();
    }
};

%include "snmpbulkget.i"
%include "snmpbulkwalk.i"
%include "snmpget.i"
%include "snmpwalk.i"
%include "snmpset.i"