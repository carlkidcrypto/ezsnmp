%module netsnmp
%include "argcargv.i"
%include "stl.i"

%{
#include "snmpget.h"
%}

// Now list ANSI C/C++ declarations
std::vector<std::string> snmpget(const std::vector<std::string> &args);