#ifndef DATATYPES_H
#define DATATYPES_H

#include <cstdint>
#include <optional>
#include <string>
#include <variant>
#include <vector>

/**
 * @brief Structure to represent an SNMP result.
 *
 * This structure holds the information retrieved from an SNMP operation,
 * including the OID, index, type, and value of the retrieved data.
 */
struct Result {
   // A single type to hold any of the converted values.
   // This makes the return type of _make_converted_value always consistent.
   using ConvertedValue =
       std::variant<int, uint32_t, uint64_t, double, std::string, std::vector<unsigned char>>;

   std::string oid = "";                ///< Object Identifier (OID) of the retrieved data.
   std::string index = "";              ///< Index of the retrieved data (if applicable).
   std::string type = "";               ///< Data type of the retrieved value.
   std::string value = "";              ///< Actual value of the retrieved data.
   ConvertedValue converted_value = ""; ///< Converted value of the type,value data.

   /**
    * @brief Converts the Result object to a string representation.
    *
    * This method generates a human-readable string representation of the
    * Result object, including all its members (oid, index, type, value, and converted_value).
    *
    * @return A string representation of the Result object.
    */
   std::string _to_string() const;

   /**
    * @brief Converts the converted_value variant to a string representation.
    *
    * Helper method to convert the std::variant converted_value to a readable string.
    *
    * @return A string representation of the converted_value.
    */
   std::string _converted_value_to_string() const;

   /**
    * @brief Factory function to obtain the appropriate ConvertedValue type based on an SNMP type
    * string.
    *
    * This function takes an SNMP type string and a value string, then attempts to convert the value
    * into the corresponding C++ type. The converted value is stored in a ConvertedValue, which is a
    * std::variant.
    *
    * @param snmpType The SNMP type as a string (e.g., "INTEGER", "OCTETSTR").
    * https://github.com/net-snmp/net-snmp/blob/02bee0fe32a4136ade3de137eef6c5acdfeed508/include/net-snmp/library/parse.h#L154-L170
    * @param value The value as a string to be converted.
    * @return ConvertedValue The value converted to the appropriate C++ type, wrapped in a
    * std::variant.
    */
   ConvertedValue _make_converted_value(std::string const& type, std::string const& value);

   /**
    * @brief Updates the converted_value member by converting the current type and value.
    *
    * This method recalculates and assigns the converted_value field using the current
    * values of the type and value members. It utilizes the private helper function
    * _make_converted_value to perform the conversion.
    *
    * Typically called after type or value has changed to ensure converted_value is up-to-date.
    */
   void update_converted_value();
};

#endif // DATATYPES_H