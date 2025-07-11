#include "datatypes.h"

#include <algorithm>
#include <sstream>
#include <string>

Result::ConvertedValue Result::_make_converted_value(std::string const& type,
                                                     std::string const& value) {
   // Convert type to lower case for case-insensitive comparison
   std::string type_lower = type;
   std::transform(type_lower.begin(), type_lower.end(), type_lower.begin(), ::tolower);

   if (type_lower == "integer" || type_lower == "integer32") {
      try {
         return std::stoi(value);
      } catch (std::exception const& e) {
         return type + " Conversion Error: " + e.what();
      }

   } else if (type_lower == "gauge32" || type_lower == "counter32") {
      return static_cast<uint32_t>(std::stoul(value));
   } else if (type_lower == "counter64") {
      return static_cast<uint64_t>(std::stoull(value));
   } else if (type_lower == "timeticks") {
      // TIMETICKS are usually represented as (ticks) days:hours:minutes:seconds.tenths
      // We'll extract the numeric value inside the parentheses
      size_t start = value.find('(');
      size_t end = value.find(')');
      if (start != std::string::npos && end != std::string::npos && end > start + 1) {
         std::string ticks_str = value.substr(start + 1, end - start - 1);
         return static_cast<uint32_t>(std::stoul(ticks_str));
      } else {
         return static_cast<uint32_t>(std::stoul(value));
      }
   } else if (type_lower == "hex-string") {
      std::vector<unsigned char> byte_vector;
      std::stringstream ss(value);
      std::string byte_str;

      // Read each space-separated hex value
      while (ss >> byte_str) {
         unsigned int byte_value;
         std::stringstream converter;
         converter << std::hex << byte_str;
         converter >> byte_value;
         byte_vector.push_back(static_cast<unsigned char>(byte_value));
      }

      return byte_vector;

   } else if (type_lower == "octetstr" || type_lower == "string" || type_lower == "objid" ||
              type_lower == "objidentity" || type_lower == "netaddr" || type_lower == "ipaddr" ||
              type_lower == "opaque" || type_lower == "bitstring" || type_lower == "nsapaddress" ||
              type_lower == "traptype" || type_lower == "notiftype" || type_lower == "objgroup" ||
              type_lower == "notifgroup" || type_lower == "modid" || type_lower == "agentcap" ||
              type_lower == "modcomp" || type_lower == "null" || type_lower == "other") {
      return "No Conversion Available"; // For these types, we return a string to indicate no
                                        // conversion
   }

   // Fallback for unknown types or specific cases not handled above
   return "Unknown Type Conversion";
}

std::string Result::_to_string() const {
   return "oid: " + this->oid + ", index: " + this->index + ", type: " + this->type +
          ", value: " + this->value;
}

void Result::update_converted_value() {
   this->converted_value = _make_converted_value(this->type, this->value);
}