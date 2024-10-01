%module datatypes
%feature("autodoc", "0");

%{
#include "datatypes.h"
%}

// Include the header file
%include "../include/datatypes.h"

// Expose the to_string method
%extend Result {
    std::string to_string() const {
        return $self->to_string();
    }
};

// Tell SWIG how to print our datatype Result in Python
%pythoncode {
    class Result:
        def __str__(self):
            return self.to_string()
};