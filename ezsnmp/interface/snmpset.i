%module netsnmp
%include <argcargv.i>
%include <stl.i>
%include "exceptionsbase.i"

%{
#include "snmpset.h"
%}

// Now list ANSI C/C++ declarations
std::vector<BaseResult> snmpset(const std::vector<std::string> &args);
