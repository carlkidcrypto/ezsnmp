#ifndef HELPERS_H
#define HELPERS_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <memory>
#include <string>
#include <vector>

#include "datatypes.h"

std::string print_variable_to_string(oid const *objid,
                                     size_t objidlen,
                                     netsnmp_variable_list const *variable);
void snmp_sess_perror_exception(char const *prog_string, netsnmp_session *ss);
void snmp_perror_exception(char const *prog_string);
std::unique_ptr<char *[]> create_argv(std::vector<std::string> const &args, int &argc);
Result parse_result(std::string const &input);
std::vector<Result> parse_results(std::vector<std::string> const &inputs);
void remove_v3_user_from_cache(std::string const &security_name_str,
                               std::string const &context_engine_id_str);
std::string print_objid_to_string(oid const *objid, size_t objidlen);
#if NETSNMP_VERSION_MAJOR < 5 || \
   (NETSNMP_VERSION_MAJOR == 5 && \
    (NETSNMP_VERSION_MINOR < 6 || \
     (NETSNMP_VERSION_MINOR == 6 && \
      NETSNMP_VERSION_PATCH <= 2 ))) 
#define NETSNMP_APPLICATION_CONFIG_TYPE "snmpapp"
void netsnmp_cleanup_session(netsnmp_session *s);
void netsnmp_get_monotonic_clock(struct timeval* tv);
#endif
#endif // HELPERS_H