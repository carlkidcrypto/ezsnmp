#ifndef SNMPBULKGET_H
#define SNMPBULKGET_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

void snmpbulkget_usage(void);
void snmpbulkget_optProc(int argc, char *const *argv, int opt);
std::vector<Result> snmpbulkget(std::vector<std::string> const &args);

#endif // SNMPBULKGET_H