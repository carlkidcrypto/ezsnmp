#ifndef SNMPGETNEXT_H
#define SNMPGETNEXT_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

void snmpgetnext_usage(void);
void snmpgetnext_optProc(int argc, char *const *argv, int opt);
std::vector<Result> snmpgetnext(std::vector<std::string> const &args);

#endif // SNMPGETNEXT_H