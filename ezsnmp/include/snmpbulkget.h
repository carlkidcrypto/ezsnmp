#ifndef SNMPBULKGET_H
#define SNMPBULKGET_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

/**
 * @brief Prints the usage information for the snmpbulkget command.
 *
 * This function displays the command-line options and usage instructions for
 * the snmpbulkget command.
 */
void snmpbulkget_usage(void);

/**
 * @brief Processes command-line options for the snmpbulkget command.
 *
 * This function handles the processing of command-line options passed to the
 * snmpbulkget command.
 *
 * @param argc The number of command-line arguments.
 * @param argv An array of C-style strings containing the command-line arguments.
 * @param opt The option character being processed.
 */
void snmpbulkget_optProc(int argc, char *const *argv, int opt);

/**
 * @brief Performs an SNMP BULK GET operation.
 *
 * This function executes an SNMP BULK GET operation with the provided arguments
 * and returns the results.
 *
 * @param args A vector of strings containing the command-line arguments for
 *             the snmpbulkget command.
 * @return A vector of Result objects containing the retrieved data.
 */
std::vector<Result> snmpbulkget(std::vector<std::string> const &args);

#endif // SNMPBULKGET_H