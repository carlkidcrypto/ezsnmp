%module ezsnmp_swig 
%include "argcargv.i"
%{
#include "snmpwalk.h"
%}

// Now list ANSI C/C++ declarations
void
snmpwalk_usage(void);
void
snmpwalk_snmp_get_and_print(netsnmp_session * ss, oid * theoid, size_t theoid_len);
static void
snmpwalk_optProc(int argc, char *const *argv, int opt);

%apply (int ARGC, char **ARGV) { (size_t argc, const char **argv) }
int snmpwalk_main(int argc, char *argv[]);