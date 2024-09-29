%module ezsnmp

%{
#include "session.h"
%}

%feature("kwargs") Session::Session;

// Now list ANSI C/C++ declarations
%include "../include/session.h"