#ifndef SNMPBULKGET_H
#define SNMPBULKGET_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

#include "datatypes.h"

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
 * @param init_app_name A string representing the initial application name.
 * @return A vector of Result objects containing the retrieved data.
 *
 * @note The -C sub-options (e.g. -Cr, -Cn) must have their value concatenated
 *       with the flag in the same string element. For example, use "-Cr10" not
 *       "-Cr", "10" as separate elements. Passing them as separate elements will
 *       raise a ParseErrorBase exception.
 *
 * @throws ParseErrorBase if command-line argument parsing fails (e.g. missing
 *         number for -Cr or -Cn options, or unknown -C flag).
 * @throws TimeoutErrorBase if the SNMP agent does not respond.
 * @throws PacketErrorBase if the SNMP response contains an error.
 */
std::vector<Result> snmpbulkget(std::vector<std::string> const &args,
                                std::string const &init_app_name);

#endif // SNMPBULKGET_H