%module netsnmp
%include <argcargv.i>
%include <stl.i>
%include "exceptionsbase.i"

%{
#include "snmpbulkget.h"
%}

// Now list ANSI C/C++ declarations
std::vector<BaseResult> snmpbulkget(const std::vector<std::string> &args);