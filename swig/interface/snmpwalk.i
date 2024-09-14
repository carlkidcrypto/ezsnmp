%module ezsnmp_swig 
%include "argcargv.i"
%include "stl.i"
%template(_string_list) std::vector< std::string >;
%apply (int ARGC, char **ARGV) { (int argc, char *argv[]) };
%{
#include "snmpwalk.h"
%}

// Now list ANSI C/C++ declarations
void snmpwalk_usage(void);
std::vector<std::string> snmpwalk_snmp_get_and_print(netsnmp_session *ss, oid *theoid, size_t theoid_len);
void snmpwalk_optProc(int argc, char *const *argv, int opt);
std::vector<std::string> snmpwalk(int argc, char *argv[]);    
