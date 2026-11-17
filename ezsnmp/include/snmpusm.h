#ifndef EZSNMP_SNMPUSM_H
#define EZSNMP_SNMPUSM_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

#include "datatypes.h"

/**
 * @brief Prints the usage information for the snmpusm command.
 *
 * This function displays the command-line options and usage instructions for
 * the snmpusm command.
 */
void snmpusm_usage(void);

/**
 * @brief Processes command-line options for the snmpusm command.
 *
 * This function handles the processing of command-line options passed to the
 * snmpusm command.
 *
 * @param argc The number of command-line arguments.
 * @param argv An array of C-style strings containing the command-line arguments.
 * @param opt The option character being processed.
 */
void snmpusm_optProc(int argc, char *const *argv, int opt);

/**
 * @brief Performs an SNMPv3 USM user management operation.
 *
 * This function provides a C++ interface to the Net-SNMP snmpusm utility,
 * supporting create, delete, activate, deactivate, cloneFrom, passwd, and
 * changekey operations.
 *
 * @param args A vector of strings containing the command-line arguments for
 *             the snmpusm command.
 * @param init_app_name A string representing the initial application name.
 * @return A vector of strings containing the status/output lines.
 */
std::vector<std::string> snmpusm(std::vector<std::string> const &args,
                                 std::string const &init_app_name);

#endif // EZSNMP_SNMPUSM_H
