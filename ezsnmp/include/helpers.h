#ifndef HELPERS_H
#define HELPERS_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <memory>
#include <string>
#include <vector>

#include "datatypes.h"

std::string print_variable_to_string(const oid *objid, size_t objidlen,
                                     const netsnmp_variable_list *variable);
std::unique_ptr<char *[]> create_argv(const std::vector<std::string> &args, int &argc);
Result parse_result(const std::string &input);
std::vector<Result> parse_results(const std::vector<std::string> &inputs);

#endif  // HELPERS_H