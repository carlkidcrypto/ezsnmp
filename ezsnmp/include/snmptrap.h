#ifndef SNMPTRAP_H
#define SNMPTRAP_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

#include "datatypes.h"

void snmptrap_usage(void);
void snmptrap_optProc(int argc, char *const *argv, int opt);
int snmp_input(int operation, netsnmp_session *session, int reqid, netsnmp_pdu *pdu, void *magic);
int snmptrap(const std::vector<std::string> &args);

#endif  // SNMPTRAP_H