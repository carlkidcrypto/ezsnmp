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
   template<typename T>
   struct ConvertedValue {
       T value;
   };

   // Helper function to deduce type based on SNMP type string
   template<typename T = void>
   struct TypeSelector;

   template<>
   struct TypeSelector<int> {
       static constexpr const char* type_name = "INTEGER";
   };

   template<>
   struct TypeSelector<std::string> {
       static constexpr const char* type_name = "STRING";
   };

   template<>
   struct TypeSelector<uint64_t> {
       static constexpr const char* type_name = "COUNTER64";
   };

   template<>
   struct TypeSelector<uint32_t> {
       static constexpr const char* type_name = "GAUGE";
   };

   template<>
   struct TypeSelector<double> {
       static constexpr const char* type_name = "TIMETICKS";
   };

   // Factory function to get the proper ConvertedValue type based on SNMP type string
   static auto make_converted_value(const std::string& type, const std::string& value) {
       if (type == "INTEGER" || type == "INTEGER32") {
           return ConvertedValue<int>{std::stoi(value)};
       } else if (type == "UINTEGER" || type == "UNSIGNED32" || type == "GAUGE" || type == "COUNTER") {
           return ConvertedValue<uint32_t>{static_cast<uint32_t>(std::stoul(value))};
       } else if (type == "COUNTER64") {
           return ConvertedValue<uint64_t>{static_cast<uint64_t>(std::stoull(value))};
       } else if (type == "TIMETICKS") {
           return ConvertedValue<double>{std::stod(value)};
       } else if (type == "OCTETSTR" || type == "STRING" || type == "OBJID" || type == "OBJIDENTITY" ||
                  type == "NETADDR" || type == "IPADDR" || type == "OPAQUE" || type == "BITSTRING" ||
                  type == "NSAPADDRESS" || type == "TRAPTYPE" || type == "NOTIFTYPE" || type == "OBJGROUP" ||
                  type == "NOTIFGROUP" || type == "MODID" || type == "AGENTCAP" || type == "MODCOMP") {
           return ConvertedValue<std::string>{value};
       } else if (type == "NULL") {
           return ConvertedValue<std::string>{"NULL"};
       } else if (type == "OTHER") {
           return ConvertedValue<std::string>{"OTHER"};
       }
       // fallback
       return ConvertedValue<std::string>{value};
   }

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