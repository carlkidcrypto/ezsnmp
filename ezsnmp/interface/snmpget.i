%module ezsnmp
%include "argcargv.i"
%include "stl.i"
%apply (int ARGC, char **ARGV) { (int argc, char *argv[]) };
%{
#include "snmpget.h"
%}

// Now list ANSI C/C++ declarations
std::vector<std::string> snmpget(int argc, char *argv[]);