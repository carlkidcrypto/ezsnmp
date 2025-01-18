%module netsnmp
%include "argcargv.i"
%include "stl.i"
%include "exceptions.i"

%{
#include "snmpget.h"
%}

// Now list ANSI C/C++ declarations
std::vector<Result> snmpget(std::vector<std::string> const &args);
