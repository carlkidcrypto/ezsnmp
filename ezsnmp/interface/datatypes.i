%module datatypes
%feature("autodoc", "0");

%include "std_string.i"

%{
#include "datatypes.h"
%}

// Define the typemap for the 'Result *' type
%typemap(out) Result * {
    if ($1) {
        std::string result_str = $1->to_string();
        $result = PyUnicode_FromString(result_str.c_str());
    } else {
        $result = Py_None;
        Py_INCREF(Py_None);
    }
};

// Include the header file
%include "../include/datatypes.h"

// Explicitly define the __str__ method
%extend Result {
    const char *__str__() {
        return $self->to_string().c_str();
    }
};