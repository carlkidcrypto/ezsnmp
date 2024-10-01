%module netsnmp
%include "argcargv.i"
%include "stl.i"

%{
#include "snmpset.h"
%}

// Now list ANSI C/C++ declarations
int snmpset(int argc, std::unique_ptr<char *[]> &argv); 
