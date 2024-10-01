%module netsnmp
%include "argcargv.i"
%include "stl.i"

%{
#include "snmpwalk.h"
%}

// Now list ANSI C/C++ declarations
std::vector<std::string> snmpwalk(const std::vector<std::string> &args);
