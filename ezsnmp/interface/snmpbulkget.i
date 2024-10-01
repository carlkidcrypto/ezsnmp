%module netsnmp
%include "argcargv.i"
%include "stl.i"

%{
#include "snmpbulkget.h"
%}

// Now list ANSI C/C++ declarations
std::vector<std::string> snmpbulkget(const std::vector<std::string> &args);