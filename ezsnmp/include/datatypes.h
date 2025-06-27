#ifndef DATATYPES_H
#define DATATYPES_H

#include <cstdint> // For uint64_t, uint32_t
#include <string>
#include <variant> // For std::variant

// A single type to hold any of the converted values.
// This makes the return type of make_converted_value always consistent.
using ConvertedValue = std::variant<int, uint32_t, uint64_t, double, std::string>;

/**
 * @brief Factory function to obtain the appropriate ConvertedValue type based on an SNMP type
 * string.
 *
 * This function takes an SNMP type string and a value string, then attempts to convert the value
 * into the corresponding C++ type. The converted value is stored in a ConvertedValue, which is a
 * std::variant.
 *
 * @param snmpType The SNMP type as a string (e.g., "INTEGER", "OCTETSTR").
 * https://github.com/net-snmp/net-snmp/blob/02bee0fe32a4136ade3de137eef6c5acdfeed508/include/net-snmp/library/parse.h
 * @param value The value as a string to be converted.
 * @return ConvertedValue The value converted to the appropriate C++ type, wrapped in a
 * std::variant.
 */
ConvertedValue make_converted_value(std::string const& type, std::string const& value);

/**
 * @brief Structure to represent an SNMP result.
 *
 * This structure holds the information retrieved from an SNMP operation,
 * including the OID, index, type, and value of the retrieved data.
 */
struct Result {
   std::string oid = "";   ///< Object Identifier (OID) of the retrieved data.
   std::string index = ""; ///< Index of the retrieved data (if applicable).
   std::string type = "";  ///< Data type of the retrieved value.
   std::string value = ""; ///< Actual value of the retrieved data.
   ConvertedValue converted_value = make_converted_value(type, value);

   /**
    * @brief Converts the Result object to a string representation.
    *
    * This method generates a human-readable string representation of the
    * Result object, including all its members.
    *
    * @return A string representation of the Result object.
    */
   std::string to_string() const;
};

#endif // DATATYPES_H