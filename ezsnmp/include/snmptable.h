#ifndef SNMPTABLE_H
#define SNMPTABLE_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

#include "datatypes.h"

/**
 * @brief Queries and formats an SNMP table from a remote entity.
 *
 * This function provides a C++ interface to the Net-SNMP snmptable utility,
 * walking an SNMP table using GETBULK or GETNEXT requests and returning the
 * formatted table output.
 *
 * @param args A vector of strings containing the command-line arguments for
 *             the snmptable command.
 * @param init_app_name A string representing the initial application name.
 * @return A vector of strings containing the formatted SNMP table output.
 */
std::vector<std::string> snmptable(std::vector<std::string> const &args,
                                   std::string const &init_app_name);

#endif // SNMPTABLE_H
