#ifndef SNMPGET_H
#define SNMPGET_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

#include "sessionbase.h"

/**
 * @brief Prints the usage information for the snmpget command.
 *
 * This function displays the command-line options and usage instructions for
 * the snmpget command.
 */
void snmpget_usage(void);

/**
 * @brief Processes command-line options for the snmpget command.
 *
 * This function handles the processing of command-line options passed to the
 * snmpget command.
 *
 * @param argc The number of command-line arguments.
 * @param argv An array of C-style strings containing the command-line arguments.
 * @param opt The option character being processed.
 */
void snmpget_optProc(int argc, char *const *argv, int opt);

/**
 * @brief Performs an SNMP GET operation.
 *
 * This function executes an SNMP GET operation with the provided arguments
 * and returns the results.
 *
 * @param args A vector of strings containing the command-line arguments for
 *             the snmpget command.
 * @return A vector of Result objects containing the retrieved data.
 */
std::vector<Result> snmpget(std::vector<std::string> const &args);

#endif // SNMPGET_H