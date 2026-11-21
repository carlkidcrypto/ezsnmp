#ifndef SNMPDF_H
#define SNMPDF_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

#include "datatypes.h"

/**
 * @brief Displays disk space usage on a network entity via SNMP.
 *
 * This function provides a C++ interface to the Net-SNMP snmpdf utility,
 * querying HOST-RESOURCES-MIB::hrStorageTable or UCD-SNMP-MIB::dskTable (-Cu)
 * and supporting human-readable binary (-Ch) and SI (-CH) unit formatting.
 *
 * @param args A vector of strings containing the command-line arguments for
 *             the snmpdf command.
 * @param init_app_name A string representing the initial application name.
 * @return A vector of strings containing the formatted disk usage table lines
 *         (header followed by one line per filesystem/partition).
 */
std::vector<std::string> snmpdf(std::vector<std::string> const &args,
                                std::string const &init_app_name);

#endif // SNMPDF_H
