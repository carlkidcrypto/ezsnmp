#ifndef SNMPBULKWALK_H
#define SNMPBULKWALK_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

#include "datatypes.h"

/**
 * @brief Prints the usage information for the snmpbulkwalk command.
 *
 * This function displays the command-line options and usage instructions for
 * the snmpbulkwalk command.
 */
void snmpbulkwalk_usage(void);

/**
 * @brief Performs an SNMP GET operation and prints the results.
 *
 * This function performs an SNMP GET operation using the provided SNMP session
 * and OID, and then prints the retrieved data to the console.
 *
 * @param ss Pointer to the SNMP session.
 * @param theoid Pointer to the OID to retrieve.
 * @param theoid_len Length of the OID.
 * @return A vector of strings containing the printed output.
 */
std::vector<std::string> snmpbulkwalk_snmp_get_and_print(netsnmp_session *ss,
                                                         oid *theoid,
                                                         size_t theoid_len);

/**
 * @brief Processes command-line options for the snmpbulkwalk command.
 *
 * This function handles the processing of command-line options passed to the
 * snmpbulkwalk command.
 *
 * @param argc The number of command-line arguments.
 * @param argv An array of C-style strings containing the command-line arguments.
 * @param opt The option character being processed.
 */
void snmpbulkwalk_optProc(int argc, char *const *argv, int opt);

/**
 * @brief Performs an SNMP BULK WALK operation.
 *
 * This function executes an SNMP BULK WALK operation with the provided arguments
 * and returns the results.
 *
 * @param args A vector of strings containing the command-line arguments for
 *             the snmpbulkwalk command.
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
std::vector<Result> snmpbulkwalk(std::vector<std::string> const &args,
                                 std::string const &init_app_name);

#endif // SNMPBULKWALK_H