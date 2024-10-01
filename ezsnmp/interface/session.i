%module session
%feature("autodoc", "0");
%include "stl.i"
%template(_string_list) std::vector< std::string >;
%feature("kwargs") Session::Session;

%{
#include "session.h"
%}

// Now list ANSI C/C++ declarations
%include "../include/session.h"