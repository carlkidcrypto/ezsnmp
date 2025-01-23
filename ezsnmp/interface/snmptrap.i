%module netsnmp
%include <argcargv.i>
%include <stl.i>
%include "exceptionsbase.i"

%{
#include "snmptrap.h"
%}

// Now list ANSI C/C++ declarations
int snmptrap(const std::vector<std::string> &args);
