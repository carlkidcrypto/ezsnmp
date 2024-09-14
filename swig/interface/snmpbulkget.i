%module ezsnmp_swig 
%include "argcargv.i"
%include "stl.i"
%template(_string_list) std::vector< std::string >;
%apply (int ARGC, char **ARGV) { (int argc, char *argv[]) };
%{
#include "snmpbulkget.h"
%}

// Now list ANSI C/C++ declarations
int snmpbulkget(int argc, char *argv[]);