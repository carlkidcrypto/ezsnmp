%module sessionbase
%feature("autodoc", "0");

%include <stl.i>
%include "datatypes.i"
%include "exceptionsbase.i"

%feature("kwargs") SessionBase::SessionBase;
%feature("python:annotations", "c");

// Tell SWIG how to handle our special return type(s) from C++
%template(_string_list) std::vector<std::string>;
%template(_result_list) std::vector<Result>;

%{
#include "sessionbase.h"
%}

// Now list ANSI C/C++ declarations
%include "../include/sessionbase.h"