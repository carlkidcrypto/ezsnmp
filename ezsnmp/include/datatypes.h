#ifndef DATATYPES_H
#define DATATYPES_H

#include <string>

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