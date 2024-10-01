%module netsnmp
%include "argcargv.i"
%include "stl.i"

%{
#include "snmpbulkwalk.h"
%}

// Now list ANSI C/C++ declarations
std::vector<std::string> snmpbulkwalk(const std::vector<std::string> &args);