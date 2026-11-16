#ifndef SNMPSTATUS_H
#define SNMPSTATUS_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

#include "datatypes.h"

/**
 * @brief Retrieves status information from an SNMP network entity.
 *
 * This function provides a C++ interface to the Net-SNMP snmpstatus utility,
 * querying system description, uptime, IP packet statistics, and interface
 * status/packet counters.
 *
 * @param args A vector of strings containing the command-line arguments for
 *             the snmpstatus command.
 * @param init_app_name A string representing the initial application name.
 * @return A vector of strings containing the formatted status summary lines.
 */
std::vector<std::string> snmpstatus(std::vector<std::string> const &args,
                                    std::string const &init_app_name);

#endif // SNMPSTATUS_H
