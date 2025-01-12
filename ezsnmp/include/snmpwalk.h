#ifndef SNMPWALK_H
#define SNMPWALK_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

#include "datatypes.h"

/**
 * @brief Prints the usage information for the snmpwalk command.
 *
 * This function displays the command-line options and usage instructions for
 * the snmpwalk command.
 */
void snmpwalk_usage(void);

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
std::vector<std::string> snmpwalk_snmp_get_and_print(netsnmp_session *ss,
                                                     oid *theoid,
                                                     size_t theoid_len);

/**
 * @brief Processes command-line options for the snmpwalk command.
 *
 * This function handles the processing of command-line options passed to the
 * snmpwalk command.
 *
 * @param argc The number of command-line arguments.
 * @param argv An array of C-style strings containing the command-line arguments.
 * @param opt The option character being processed.
 */
void snmpwalk_optProc(int argc, char *const *argv, int opt);

/**
 * @brief Performs an SNMP WALK operation.
 *
 * This function executes an SNMP WALK operation with the provided arguments
 * and returns the results.
 *
 * @param args A vector of strings containing the command-line arguments for
 *             the snmpwalk command.
 * @return A vector of Result objects containing the retrieved data.
 */
std::vector<Result> snmpwalk(std::vector<std::string> const &args);

#endif // SNMPWALK_H