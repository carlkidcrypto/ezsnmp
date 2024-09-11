%module ezsnmp_swig 
%include "argcargv.i"
%{
#include "snmpwalk.h"
%}

// Now list ANSI C/C++ declarations
void snmpwalk_usage(void);
void snmpwalk_snmp_get_and_print(netsnmp_session *ss, oid *theoid, size_t theoid_len);
void snmpwalk_optProc(int argc, char *const *argv, int opt);
int snmpwalk(int argc, char *argv[]);

%apply (int ARGC, char **ARGV) { (int argc, char *argv[]) }
int snmpwalk(int argc, char *argv[]);