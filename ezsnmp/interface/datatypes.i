%module datatypes
%feature("autodoc", "0");

%include <std_string.i>

%{
#include "datatypes.h"
%}

// Typemap to remove extra quotes when converting std::string to Python
%typemap(out) std::string {
    $result = PyUnicode_FromString($1.c_str());
}

// Include the header file
%include "../include/datatypes.h"