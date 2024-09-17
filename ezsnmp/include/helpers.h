#ifndef HELPERS_H
#define HELPERS_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
#include <string>

std::string print_variable_to_string(const oid *objid, size_t objidlen, const netsnmp_variable_list *variable);
void add_first_arg(int *argc, char ***argv);

#endif // HELPERS_H