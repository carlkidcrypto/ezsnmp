#include "datatypes.h"

#include <algorithm>
#include <cctype> // For ::isdigit
#include <regex>  // For regex parsing of numeric values
#include <sstream>
#include <string>

Result::ConvertedValue Result::_make_converted_value(std::string const& type,
                                                     std::string const& value) {
   // Convert type to lower case for case-insensitive comparison
   std::string type_lower = type;
   std::transform(type_lower.begin(), type_lower.end(), type_lower.begin(), ::tolower);

   // Helper to extract numeric part from strings like "up(1)" or "60000 milli-seconds"
   auto extract_numeric_value = [](std::string const& val_str) {
      std::string numeric_part = "";
      std::smatch match;
      // Try to match numbers inside parentheses, or just a number at the beginning
      if (std::regex_search(val_str, match, std::regex("\\((\\d+)\\)"))) {
         numeric_part = match[1].str();
      } else if (std::regex_search(val_str, match,
                                   std::regex("^\\s*(-?\\d+)"))) { // Match optional leading space,
                                                                   // optional minus, then digits
         numeric_part = match[1].str();
      }
      return numeric_part;
   };

   if (type_lower == "integer" || type_lower == "integer32") {
      std::string numeric_str = extract_numeric_value(value);
      if (numeric_str.empty() && !value.empty()) { // If no numeric part extracted but value isn't
                                                   // empty, try direct conversion
         numeric_str = value;
      } else if (value.empty()) { // Handle empty value explicitly for numeric types
         return type + " Conversion Error: Empty value for numeric type";
      }
      try {
         return std::stoi(numeric_str);
      } catch (std::exception const& e) {
         return type + " Conversion Error: " + e.what();
      }

   } else if (type_lower == "gauge32" || type_lower == "counter32") {
      std::string numeric_str = extract_numeric_value(value);
      if (numeric_str.empty() && !value.empty()) {
         numeric_str = value;
      } else if (value.empty()) {
         return type + " Conversion Error: Empty value for numeric type";
      }
      try {
         return static_cast<uint32_t>(std::stoul(numeric_str));
      } catch (std::exception const& e) {
         return type + " Conversion Error: " + e.what();
      }

   } else if (type_lower == "counter64") {
      std::string numeric_str = extract_numeric_value(value);
      if (numeric_str.empty() && !value.empty()) {
         numeric_str = value;
      } else if (value.empty()) {
         return type + " Conversion Error: Empty value for numeric type";
      }
      try {
         return static_cast<uint64_t>(std::stoull(numeric_str));
      } catch (std::exception const& e) {
         return type + " Conversion Error: " + e.what();
      }

   } else if (type_lower == "timeticks") {
      std::string numeric_str = extract_numeric_value(value);
      if (numeric_str.empty() && !value.empty()) {
         numeric_str = value;
      } else if (value.empty()) {
         return type + " Conversion Error: Empty value for numeric type";
      }
      try {
         return static_cast<uint32_t>(std::stoul(numeric_str));
      } catch (std::exception const& e) {
         return type + " Conversion Error: " + e.what();
      }
   } else if (type_lower == "hex-string") {
      std::vector<unsigned char> byte_vector;
      std::stringstream ss(value);
      std::string byte_str;

      // Read each space-separated hex value
      while (ss >> byte_str) {
         // Remove any non-hex characters (like ':', although not in your example)
         byte_str.erase(std::remove_if(byte_str.begin(), byte_str.end(),
                                       [](char c) { return !std::isxdigit(c); }),
                        byte_str.end());
         if (byte_str.empty()) {
            continue; // Skip empty parts
         }

         unsigned int byte_value;
         std::stringstream converter;
         converter << std::hex << byte_str;
         if (converter >> byte_value) { // Check if conversion was successful
            byte_vector.push_back(static_cast<unsigned char>(byte_value));
         } else {
            // Handle malformed hex string parts
            return type + " Conversion Error: Malformed hex part '" + byte_str + "'";
         }
      }
      return byte_vector;

   } else if (type_lower == "octetstr" || type_lower == "string" || type_lower == "oid" ||
              type_lower == "objid" || // Treat OID as string representation
              type_lower == "objidentity" || type_lower == "ipaddress" ||
              type_lower == "network address" || // Handle IpAddress as string
              type_lower == "opaque" || type_lower == "bitstring" || type_lower == "nsapaddress" ||
              type_lower == "traptype" || type_lower == "notiftype" || type_lower == "objgroup" ||
              type_lower == "notifgroup" || type_lower == "modid" || type_lower == "agentcap" ||
              type_lower == "modcomp" || type_lower == "null" || type_lower == "other") {
      // For these types, the 'value' string itself is the most appropriate representation
      // for 'converted_value' if no further specific C++ type conversion is needed.
      // We can return the value directly, or a fixed string like "No Conversion Available".
      // Returning the value makes it more useful.
      return value; // Return the original string value
   }

   // Fallback for truly unknown types
   return "Unknown Type Conversion";
}

std::string Result::_to_string() const {
   return "oid: " + this->oid + ", index: " + this->index + ", type: " + this->type +
          ", value: " + this->value;
}

void Result::update_converted_value() {
   this->converted_value = _make_converted_value(this->type, this->value);
}