#ifndef SNMPSET_H
#define SNMPSET_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
#include <string>
#include <vector>

void snmpset_usage(void);
void snmpset_optProc(int argc, char *const *argv, int opt);
int snmpset(int argc, char *argv[]);

#endif // SNMPSET_H