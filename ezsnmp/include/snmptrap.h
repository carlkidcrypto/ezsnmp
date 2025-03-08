#ifndef SNMPTRAP_H
#define SNMPTRAP_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <string>
#include <vector>

#include "datatypes.h"

/**
 * @brief Prints the usage information for the snmptrap command.
 *
 * This function displays the command-line options and usage instructions for
 * the snmptrap command.
 */
void snmptrap_usage(void);

/**
 * @brief Processes command-line options for the snmptrap command.
 *
 * This function handles the processing of command-line options passed to the
 * snmptrap command.
 *
 * @param argc The number of command-line arguments.
 * @param argv An array of C-style strings containing the command-line arguments.
 * @param opt The option character being processed.
 */
void snmptrap_optProc(int argc, char *const *argv, int opt);

/**
 * @brief Callback function for processing incoming SNMP messages.
 *
 * This function is used as a callback to handle incoming SNMP messages, such as
 * traps or responses.
 *
 * @param operation The SNMP operation code (e.g., SNMP_MSG_TRAP).
 * @param session Pointer to the SNMP session.
 * @param reqid The request ID.
 * @param pdu Pointer to the SNMP PDU (protocol data unit).
 * @param magic Pointer to user-defined data.
 * @return An integer indicating the result of the processing.
 */
int snmp_input(int operation, netsnmp_session *session, int reqid, netsnmp_pdu *pdu, void *magic);

/**
 * @brief Sends an SNMP TRAP.
 *
 * This function sends an SNMP TRAP with the provided arguments.
 *
 * @param args A vector of strings containing the command-line arguments for
 *             the snmptrap command.
 * @return An integer indicating the result of the TRAP operation.
 */
int snmptrap(std::vector<std::string> const &args);

#endif // SNMPTRAP_H