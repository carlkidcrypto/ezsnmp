#ifndef DATATYPES_H
#define DATATYPES_H

#include <string>
#include <variant> // For std::variant
#include <cstdint> // For uint64_t, uint32_t

// A single type to hold any of the converted values.
// This makes the return type of make_converted_value always consistent.
using ConvertedValue = std::variant<int, uint32_t, uint64_t, double, std::string>;

// Factory function to get the proper ConvertedValue type based on SNMP type string
// It takes an SNMP type string and a value string, then tries to convert the value
// into the appropriate C++ type, storing it in a ConvertedValue (std::variant).
ConvertedValue make_converted_value(std::string const& type, std::string const& value) {
   if (type == "INTEGER" || type == "INTEGER32") {
      return std::stoi(value);
   } else if (type == "UINTEGER" || type == "UNSIGNED32" || type == "GAUGE" || type == "COUNTER") {
      return static_cast<uint32_t>(std::stoul(value));
   } else if (type == "COUNTER64") {
      return static_cast<uint64_t>(std::stoull(value));
   } else if (type == "TIMETICKS") {
      return std::stod(value);
   } else if (type == "OCTETSTR" || type == "STRING" || type == "OBJID" || type == "OBJIDENTITY" ||
              type == "NETADDR" || type == "IPADDR" || type == "OPAQUE" || type == "BITSTRING" ||
              type == "NSAPADDRESS" || type == "TRAPTYPE" || type == "NOTIFTYPE" ||
              type == "OBJGROUP" || type == "NOTIFGROUP" || type == "MODID" || type == "AGENTCAP" ||
              type == "MODCOMP" || type == "NULL" || type == "OTHER") {
      return value;
   }

   // Fallback for unknown types or specific cases not handled above
   return value;
}

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