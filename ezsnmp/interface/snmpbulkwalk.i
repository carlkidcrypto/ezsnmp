%module netsnmp
%include "argcargv.i"
%include "stl.i"

%{
#include "snmpbulkwalk.h"
%}

// Now list ANSI C/C++ declarations
std::vector<std::string> snmpbulkwalk(int argc, std::unique_ptr<char *[]> &argv);