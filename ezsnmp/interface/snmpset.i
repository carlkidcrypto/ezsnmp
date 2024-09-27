%module ezsnmp
%include "argcargv.i"
%include "stl.i"
%apply (int ARGC, char **ARGV) { (int argc, char *argv[]) };
%{
#include "snmpset.h"
%}

// Now list ANSI C/C++ declarations
int snmpset(int argc, char *argv[]);  
