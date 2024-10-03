#ifndef SNMPBULKWALK_H
#define SNMPBULKWALK_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

void snmpbulkwalk_usage(void);
std::vector<std::string> snmpbulkwalk_snmp_get_and_print(netsnmp_session *ss, oid *theoid,
                                                         size_t theoid_len);
void snmpbulkwalk_optProc(int argc, char *const *argv, int opt);
std::vector<std::string> snmpbulkwalk(const std::vector<std::string> &args);

#endif  // SNMPBULKWALK_H