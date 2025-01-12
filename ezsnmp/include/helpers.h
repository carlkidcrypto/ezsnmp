#ifndef HELPERS_H
#define HELPERS_H

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <memory>
#include <string>
#include <vector>

#include "datatypes.h"

/**
 * @brief Converts SNMP variable bindings to a string representation.
 *
 * This function takes an SNMP variable binding (oid, objidlen, variable) and
 * converts it into a human-readable string representation.
 *
 * @param objid Pointer to the object identifier (OID).
 * @param objidlen Length of the OID.
 * @param variable Pointer to the netsnmp_variable_list containing the variable binding.
 * @return A string representation of the variable binding.
 */
std::string print_variable_to_string(oid const *objid,
                                     size_t objidlen,
                                     netsnmp_variable_list const *variable);

/**
 * @brief Throws an exception with SNMP session error information.
 *
 * This function throws an exception that includes the provided program string
 * and the error information from the SNMP session.
 *
 * @param prog_string A string describing the program or context.
 * @param ss Pointer to the netsnmp_session.
 */
void snmp_sess_perror_exception(char const *prog_string, netsnmp_session *ss);

/**
 * @brief Throws an exception with SNMP error information.
 *
 * This function throws an exception that includes the provided program string
 * and the SNMP error information.
 *
 * @param prog_string A string describing the program or context.
 */
void snmp_perror_exception(char const *prog_string);

/**
 * @brief Creates an array of C-style strings from a vector of strings.
 *
 * This function takes a vector of strings and creates an array of C-style strings
 * (char*) suitable for use as command-line arguments.
 *
 * @param args A vector of strings.
 * @param argc An integer to store the number of arguments.
 * @return A unique pointer to the array of C-style strings.
 */
std::unique_ptr<char *[]> create_argv(std::vector<std::string> const &args, int &argc);

/**
 * @brief Parses a single SNMP result string.
 *
 * This function parses a string containing an SNMP result and extracts the relevant
 * information into a Result object.
 *
 * @param input The input string containing the SNMP result.
 * @return A Result object containing the parsed information.
 */
Result parse_result(std::string const &input);

/**
 * @brief Parses multiple SNMP result strings.
 *
 * This function parses a vector of strings, each containing an SNMP result,
 * and extracts the relevant information into a vector of Result objects.
 *
 * @param inputs A vector of strings containing SNMP results.
 * @return A vector of Result objects containing the parsed information.
 */
std::vector<Result> parse_results(std::vector<std::string> const &inputs);

/**
 * @brief Removes SNMP v3 user information from the cache.
 *
 * This function removes the SNMP v3 user information associated with the given
 * security name and context engine ID from the internal cache.
 *
 * @param security_name_str The security name of the user.
 * @param context_engine_id_str The context engine ID.
 */
void remove_v3_user_from_cache(std::string const &security_name_str,
                               std::string const &context_engine_id_str);

/**
 * @brief Converts an OID to its string representation.
 *
 * This function takes an OID (object identifier) and converts it into a human-readable
 * string representation.
 *
 * @param objid Pointer to the object identifier (OID).
 * @param objidlen Length of the OID.
 * @return A string representation of the OID.
 */
std::string print_objid_to_string(oid const *objid, size_t objidlen);

#endif // HELPERS_H