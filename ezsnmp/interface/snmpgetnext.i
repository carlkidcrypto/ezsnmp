%module netsnmp
%include <argcargv.i>
%include <stl.i>
%include "exceptions.i"

%{
#include "snmpgetnext.h"
%}

// Now list ANSI C/C++ declarations
std::vector<Result> snmpgetnext(std::vector<std::string> const &args);