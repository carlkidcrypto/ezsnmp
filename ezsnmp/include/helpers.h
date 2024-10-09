#ifndef HELPERS_H
#define HELPERS_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <memory>
#include <string>
#include <vector>

#include "datatypes.h"

std::string print_variable_to_string(oid const *objid, size_t objidlen,
                                     netsnmp_variable_list const *variable);
std::unique_ptr<char *[]> create_argv(std::vector<std::string> const &args, int &argc);
Result parse_result(std::string const &input);
std::vector<Result> parse_results(std::vector<std::string> const &inputs);

#endif // HELPERS_H