#ifndef SNMPWALK_H
#define SNMPWALK_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

#include "datatypes.h"

void snmpwalk_usage(void);
std::vector<std::string> snmpwalk_snmp_get_and_print(netsnmp_session *ss,
                                                     oid *theoid,
                                                     size_t theoid_len);
void snmpwalk_optProc(int argc, char *const *argv, int opt);
std::vector<Result> snmpwalk(std::vector<std::string> const &args);

#endif // SNMPWALK_H