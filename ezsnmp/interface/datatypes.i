%module datatypes
%feature("autodoc", "0");

%include "stl.i"
%include "datatypes.i" // Include it again for SWIG to process

// Tell SWIG how to handle our special return type from C++
%template(_result_list) std::vector<Result>;

%{
#include "datatypes.h"
%}

// Now list ANSI C/C++ declarations
%include "../include/datatypes.h"