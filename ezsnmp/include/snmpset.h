#ifndef SNMPSET_H
#define SNMPSET_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

/**
 * @brief Prints the usage information for the snmpset command.
 *
 * This function displays the command-line options and usage instructions for
 * the snmpset command.
 */
void snmpset_usage(void);

/**
 * @brief Processes command-line options for the snmpset command.
 *
 * This function handles the processing of command-line options passed to the
 * snmpset command.
 *
 * @param argc The number of command-line arguments.
 * @param argv An array of C-style strings containing the command-line arguments.
 * @param opt The option character being processed.
 */
void snmpset_optProc(int argc, char *const *argv, int opt);

/**
 * @brief Performs an SNMP SET operation.
 *
 * This function executes an SNMP SET operation with the provided arguments
 * and returns the results.
 *
 * @param args A vector of strings containing the command-line arguments for
 *             the snmpset command.
 * @return A vector of Result objects containing the results of the SET operation.
 */
std::vector<Result> snmpset(std::vector<std::string> const &args);

#endif // SNMPSET_H