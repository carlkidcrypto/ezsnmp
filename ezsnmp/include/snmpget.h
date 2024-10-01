#ifndef SNMPGET_H
#define SNMPGET_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
#include <string>
#include <vector>
#include <memory>

void snmpget_usage(void);
void snmpget_optProc(int argc, char *const *argv, int opt);
std::vector<std::string> snmpget(int argc, std::unique_ptr<char *[]> &argv);

#endif // SNMPGET_H