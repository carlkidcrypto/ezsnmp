%module ezsnmp_swig 
%include "argcargv.i"
%{
#include "snmpbulkwalk.h"
%}

// Now list ANSI C/C++ declarations
void snmpbulkwalk_usage(void);
void snmpbulkwalk_optProc(int argc, char *const *argv, int opt);
int snmpbulkwalk(int argc, char *argv[]);

%apply (int ARGC, char **ARGV) { (int argc, char *argv[]) }
int snmpbulkwalk(int argc, char *argv[]);