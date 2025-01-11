#ifndef SNMPGETNEXT_H
#define SNMPGETNEXT_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

/**
 * @brief Prints the usage information for the snmpgetnext command.
 *
 * This function displays the command-line options and usage instructions for
 * the snmpgetnext command.
 */
void snmpgetnext_usage(void);

/**
 * @brief Processes command-line options for the snmpgetnext command.
 *
 * This function handles the processing of command-line options passed to the
 * snmpgetnext command.
 *
 * @param argc The number of command-line arguments.
 * @param argv An array of C-style strings containing the command-line arguments.
 * @param opt The option character being processed.
 */
void snmpgetnext_optProc(int argc, char *const *argv, int opt);

/**
 * @brief Performs an SNMP GETNEXT operation.
 *
 * This function executes an SNMP GETNEXT operation with the provided arguments
 * and returns the results.
 *
 * @param args A vector of strings containing the command-line arguments for
 *             the snmpgetnext command.
 * @return A vector of Result objects containing the retrieved data.
 */
std::vector<Result> snmpgetnext(std::vector<std::string> const &args);

#endif // SNMPGETNEXT_H