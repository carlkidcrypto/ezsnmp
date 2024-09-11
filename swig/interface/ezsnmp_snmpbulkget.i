%module ezsnmp_swig 
%include "argcargv.i"
%{
#include "snmpget.h"
%}

// Now list ANSI C/C++ declarations
void snmpget_usage(void);
void snmpget_optProc(int argc, char *const *argv, int opt);
int snmpget(int argc, char *argv[]);

%apply (int ARGC, char **ARGV) { (int argc, char *argv[]) }
int snmpget(int argc, char *argv[]);