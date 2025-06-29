%module netsnmp
%include <argcargv.i>
%include <stl.i>
%include "exceptionsbase.i"

%{
#include "snmpgetnext.h"
%}

// Now list ANSI C/C++ declarations
std::vector<ResultBase> snmpgetnext(std::vector<std::string> const &args);