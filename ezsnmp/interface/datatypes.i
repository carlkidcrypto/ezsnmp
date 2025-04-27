%module datatypes
%feature("autodoc", "0");

%include <std_string.i>

%{
#include "datatypes.h"
%}

// Include the header file
%include "../include/datatypes.h"