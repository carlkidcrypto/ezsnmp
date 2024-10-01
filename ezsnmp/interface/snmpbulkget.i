%module netsnmp
%include "argcargv.i"
%include "stl.i"

%{
#include "snmpbulkget.h"
%}

// Now list ANSI C/C++ declarations
std::vector<std::string> snmpbulkget(int argc, std::unique_ptr<char *[]> &argv);