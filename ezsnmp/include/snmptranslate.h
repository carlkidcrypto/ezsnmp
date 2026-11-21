#ifndef SNMPTRANSLATE_H
#define SNMPTRANSLATE_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

#include "datatypes.h"

/**
 * @brief Translates SNMP OIDs and queries MIB definitions.
 *
 * This function provides a C++ interface to the Net-SNMP snmptranslate utility,
 * supporting OID translation, formatting options (-O, -I, -P), and MIB tree or
 * description queries (-T).
 *
 * @param args A vector of strings containing the command-line arguments for
 *             the snmptranslate command.
 * @param init_app_name A string representing the initial application name.
 * @return A vector of strings containing the translated OIDs or MIB reports.
 */
std::vector<std::string> snmptranslate(std::vector<std::string> const &args,
                                       std::string const &init_app_name);

#endif // SNMPTRANSLATE_H
