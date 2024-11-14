#ifndef SNMPGET_H
#define SNMPGET_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

#include "sessionbase.h"

void snmpget_usage(void);
void snmpget_optProc(int argc, char *const *argv, int opt);
std::vector<Result> snmpget(std::vector<std::string> const &args);

#endif // SNMPGET_H