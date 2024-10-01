%module netsnmp
%include "argcargv.i"
%include "stl.i"

%{
#include "snmpset.h"
%}

// Now list ANSI C/C++ declarations
int snmpset(const std::vector<std::string> &args);
