#include "datatypes.h"

#include <algorithm>
#include <cctype>   // For ::isspace, ::isxdigit
#include <iomanip>  // For std::setfill, std::setw
#include <iostream> // For debug prints
#include <regex>    // For regex parsing of numeric values
#include <sstream>
#include <string>

Result::ConvertedValue Result::_make_converted_value(std::string const& type,
                                                     std::string const& value) {
   // Convert type to lower case for case-insensitive comparison
   std::string type_lower = type;
   std::transform(type_lower.begin(), type_lower.end(), type_lower.begin(), ::tolower);

   // Helper to extract numeric part from strings like "up(1)" or "60000 milli-seconds" or "42"
   auto extract_numeric_value = [](std::string const& val_str) -> std::string {
      std::smatch match;
      // Try to match numbers inside parentheses, or just a number at the beginning
      if (std::regex_search(val_str, match, std::regex("\\((\\d+)\\)"))) {
         return match[1].str();
      } else if (std::regex_search(val_str, match,
                                   std::regex("^\\s*(-?\\d+)"))) { // Match optional leading space,
                                                                   // optional minus, then digits
         return match[1].str();
      }
      return val_str; // Fallback to direct value if no specific pattern matched
   };

   // Helper lambda for numeric conversions to reduce code duplication
   auto convert_numeric = [&](auto stox_func) -> Result::ConvertedValue {
      std::string numeric_str = extract_numeric_value(value);
      if (numeric_str.empty()) {
         if (value.empty()) {
            return type + " Conversion Error: Empty value for numeric type";
         }
         // Fallback to direct value if no specific pattern matched and it's not empty
         numeric_str = value;
      }
      try {
         return stox_func(numeric_str);
      } catch (std::exception const& e) {
         return type + " Conversion Error: " + e.what();
      }
   };

   if (type_lower == "integer" || type_lower == "integer32") {
      return convert_numeric([](std::string const& s) { return std::stoi(s); });
   } else if (type_lower == "gauge32" || type_lower == "counter32" || type_lower == "timeticks") {
      return convert_numeric(
          [](std::string const& s) { return static_cast<uint32_t>(std::stoul(s)); });
   } else if (type_lower == "counter64") {
      return convert_numeric(
          [](std::string const& s) { return static_cast<uint64_t>(std::stoull(s)); });
   } else if (type_lower == "hex-string") {
      std::vector<unsigned char> byte_vector;
      std::stringstream ss(value);
      std::string byte_str;

      // Handle empty value specifically for Hex-STRING as an empty vector
      if (value.empty() || std::all_of(value.begin(), value.end(), ::isspace)) {
         return byte_vector; // Return empty vector for empty/whitespace-only input
      }

      while (ss >> byte_str) {
         if (byte_str.length() > 2 ||
             byte_str.find_first_not_of("0123456789abcdefABCDEF") != std::string::npos) {
            return type + " Conversion Error: Malformed hex part '" + byte_str + "'";
         }

         unsigned int byte_value;
         std::stringstream converter;
         converter << std::hex << byte_str;
         if (!(converter >> byte_value)) {
            // This should not be reached given the validation above, but is a safeguard.
            return type + " Conversion Error: Unexpected conversion failure for '" + byte_str + "'";
         }
         byte_vector.push_back(static_cast<unsigned char>(byte_value));
      }
      return byte_vector;

   } else if (type_lower == "octetstr") {
      // Convert string to vector of unsigned chars (byte-by-byte)
      std::vector<unsigned char> byte_vector;
      byte_vector.reserve(value.length()); // Optimize allocation
      for (char c : value) {
         byte_vector.push_back(static_cast<unsigned char>(c));
      }
      return byte_vector;

   } else if (type_lower == "string" || // STRING typically represents printable text
              type_lower == "oid" || type_lower == "objid" || // OID as string representation
              type_lower == "objidentity" || type_lower == "ipaddress" ||
              type_lower == "network address" || // IP addresses as string
              type_lower == "opaque" || type_lower == "bitstring" || type_lower == "nsapaddress" ||
              type_lower == "traptype" || type_lower == "notiftype" || type_lower == "objgroup" ||
              type_lower == "notifgroup" || type_lower == "modid" || type_lower == "agentcap" ||
              type_lower == "modcomp" || type_lower == "null" || type_lower == "other") {
      // For these types, the 'value' string itself is the most appropriate representation
      // for 'converted_value' if no further specific C++ type conversion is needed.
      return value; // Return the original string value
   }

   // Fallback for truly unknown types
   return "Unknown Type Conversion";
}

std::string Result::_converted_value_to_string() const {
   // Use std::visit for type-safe, idiomatic variant handling (as suggested by Gemini review)
   return std::visit(
       [](auto&& arg) -> std::string {
          using T = std::decay_t<decltype(arg)>;

          if constexpr (std::is_same_v<T, int>) {
             return std::to_string(arg);
          } else if constexpr (std::is_same_v<T, uint32_t>) {
             return std::to_string(arg);
          } else if constexpr (std::is_same_v<T, uint64_t>) {
             return std::to_string(arg);
          } else if constexpr (std::is_same_v<T, double>) {
             return std::to_string(arg);
          } else if constexpr (std::is_same_v<T, std::string>) {
             return arg;
          } else if constexpr (std::is_same_v<T, std::vector<unsigned char>>) {
             // Convert bytes to hex string representation
             std::ostringstream oss;
             oss << "bytes[" << arg.size() << "]: ";
             for (size_t i = 0; i < std::min(arg.size(), size_t(32)); ++i) {
                oss << std::hex << std::setfill('0') << std::setw(2) << static_cast<int>(arg[i]);
                if (i < std::min(arg.size(), size_t(32)) - 1) {
                   oss << " ";
                }
             }
             if (arg.size() > 32) {
                oss << "...";
             }
             return oss.str();
          } else {
             return "<variant holds unexpected type>";
          }
       },
       converted_value);
}

std::string Result::_to_string() const {
   return "oid: " + this->oid + ", index: " + this->index + ", type: " + this->type +
          ", value: " + this->value + ", converted_value: " + _converted_value_to_string();
}

void Result::update_converted_value() {
   this->converted_value = _make_converted_value(this->type, this->value);
}