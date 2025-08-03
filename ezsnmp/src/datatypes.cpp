#include "datatypes.h"

#include <algorithm>
#include <cctype>   // For ::isspace, ::isxdigit
#include <iostream> // For debug prints
#include <regex>    // For regex parsing of numeric values
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
         numeric_str = value;     // Fallback to direct value if no specific pattern matched
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

      // Handle empty value specifically for Hex-STRING as an empty vector
      if (value.empty() || std::all_of(value.begin(), value.end(), ::isspace)) {
         return byte_vector; // Return empty vector for empty/whitespace-only input
      }

      while (ss >> byte_str) {
         // Remove any non-hex characters (like ':', although not in your example)
         // Ensure only hex characters remain for conversion
         std::string cleaned_byte_str;
         std::copy_if(byte_str.begin(), byte_str.end(), std::back_inserter(cleaned_byte_str),
                      [](char c) { return std::isxdigit(static_cast<unsigned char>(c)); });

         if (cleaned_byte_str.empty()) {
            // If a part becomes empty after cleaning (e.g., "0xG" -> "G" -> "" if not hex),
            // or if it was just "0x", we should treat it as an error for that part
            // if it was the *only* part or if it implies malformation.
            // For "0xG", "G" would be cleaned to empty, then it would skip.
            // Re-evaluate if any non-hex part should always cause an error.
            // For robustness, let's treat any non-empty but non-hex-convertible part as an error.
            // For now, if clean fails, it means the original byte_str had non-hex.
            if (!byte_str.empty() && cleaned_byte_str.empty()) {
               return type + " Conversion Error: Malformed hex part '" + byte_str + "'";
            }
            continue; // Skip parts that were just whitespace or genuinely empty
         }

         unsigned int byte_value;
         std::stringstream converter;
         converter << std::hex << cleaned_byte_str; // Use cleaned string here
         if (converter >> byte_value) {             // Check if conversion was successful
            byte_vector.push_back(static_cast<unsigned char>(byte_value));
         } else {
            // This 'else' branch should ideally not be hit if cleaned_byte_str contains only hex,
            // but as a fallback for unexpected errors in stringstream.
            return type + " Conversion Error: Unexpected conversion failure for '" +
                   cleaned_byte_str + "'";
         }
      }
      return byte_vector; // If loop finishes without error, return the collected bytes.
                          // This will be empty if no valid hex parts were found (e.g., input was "
                          // ").

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

std::string Result::_to_string() const {
   return "oid: " + this->oid + ", index: " + this->index + ", type: " + this->type +
          ", value: " + this->value;
}

void Result::update_converted_value() {
   this->converted_value = _make_converted_value(this->type, this->value);
}