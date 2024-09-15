#ifndef SNMPBULKGET_H
#define SNMPBULKGET_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

void snmpbulkget_usage(void);
void snmpbulkget_optProc(int argc, char *const *argv, int opt);
std::vector<std::string> snmpbulkget(int argc, char *argv[]);

#endif // SNMPBULKGET_H