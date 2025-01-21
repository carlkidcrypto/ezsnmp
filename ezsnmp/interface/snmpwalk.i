%module netsnmp
%include <argcargv.i>
%include <stl.i>
%include "exceptions.i"

%{
#include "snmpwalk.h"
%}

// Now list ANSI C/C++ declarations
std::vector<Result> snmpwalk(const std::vector<std::string> &args);
