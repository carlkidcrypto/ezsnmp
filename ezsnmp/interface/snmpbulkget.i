%module netsnmp
%include "argcargv.i"
%include "stl.i"
%apply (int ARGC, char **ARGV) { (int argc, char *argv[]) };
%{
#include "snmpbulkget.h"
%}

// Now list ANSI C/C++ declarations
std::vector<std::string> snmpbulkget(int argc, char *argv[]);