#ifndef SNMPBULKWALK_H
#define SNMPBULKWALK_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

void snmpbulkwalk_usage(void);
void snmpbulkwalk_snmp_get_and_print(netsnmp_session *ss, oid *theoid, size_t theoid_len);
void snmpbulkwalk_optProc(int argc, char *const *argv, int opt);
int snmpbulkwalk(int argc, char *argv[]);

#endif // SNMPBULKWALK_H