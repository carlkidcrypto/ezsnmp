%module netsnmp
%include <argcargv.i>
%include <stl.i>
%include "exceptionsbase.i"

%{
#include "snmpbulkwalk.h"
%}

// Now list ANSI C/C++ declarations
std::vector<BaseResult> snmpbulkwalk(const std::vector<std::string> &args);