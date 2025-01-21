%module netsnmp
%include <argcargv.i>
%include <stl.i>
%include "exceptions.i"

%{
#include "snmpbulkget.h"
%}

// Now list ANSI C/C++ declarations
std::vector<Result> snmpbulkget(const std::vector<std::string> &args);