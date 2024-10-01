%module netsnmp
%include "argcargv.i"
%include "stl.i"
%apply (int ARGC, char **ARGV) { (int argc, char *argv[]) };
%{
#include "snmpbulkwalk.h"
%}

// Now list ANSI C/C++ declarations
std::vector<std::string> snmpbulkwalk(int argc, char *argv[]);