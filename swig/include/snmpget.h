#ifndef SNMPGET_H
#define SNMPGET_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

void snmpget_usage(void);
void snmpget_optProc(int argc, char *const *argv, int opt);
int snmpget(int argc, char *argv[]);

#endif // SNMPGET_H