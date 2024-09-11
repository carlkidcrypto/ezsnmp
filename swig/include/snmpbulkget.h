#ifndef SNMPBULKGET_H
#define SNMPBULKGET_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

void snmpbulkget_usage(void);
void snmpbulkget_snmp_get_and_print(netsnmp_session *ss, oid *theoid, size_t theoid_len);
void snmpbulkget_optProc(int argc, char *const *argv, int opt);
int snmpbulkget(int argc, char *argv[]);

#endif // SNMPBULKGET_H