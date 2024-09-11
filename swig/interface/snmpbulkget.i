%module ezsnmp_swig 
%include "argcargv.i"
%{
#include "snmpbulkget.h"
%}

// Now list ANSI C/C++ declarations
void snmpbulkget_usage(void);
void snmpbulkget_optProc(int argc, char *const *argv, int opt);
int snmpbulkget(int argc, char *argv[]);

%apply (int ARGC, char **ARGV) { (int argc, char *argv[]) }
int snmpbulkget(int argc, char *argv[]);