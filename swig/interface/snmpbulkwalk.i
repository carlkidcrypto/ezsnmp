%module ezsnmp_swig 
%include "argcargv.i"
%include "stl.i"
%template(_string_list) std::vector< std::string >;
%apply (int ARGC, char **ARGV) { (int argc, char *argv[]) };
%{
#include "snmpbulkwalk.h"
%}

// Now list ANSI C/C++ declarations
std::vector<std::string> snmpbulkwalk(int argc, char *argv[]);