#include "datatypes.h"

#include <algorithm>
#include <string>

ResultBase::ConvertedValue ResultBase::_make_converted_value(std::string const& type,
                                                             std::string const& value) {
   // Convert type to lower case for case-insensitive comparison
   std::string type_lower = type;
   std::transform(type_lower.begin(), type_lower.end(), type_lower.begin(), ::tolower);

   if (type_lower == "integer" || type_lower == "integer32") {
      return std::stoi(value);
   } else if (type_lower == "uinteger" || type_lower == "unsigned32" || type_lower == "gauge" ||
              type_lower == "counter") {
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
      }
   } else if (type_lower == "octetstr" || type_lower == "string" || type_lower == "objid" ||
              type_lower == "objidentity" || type_lower == "netaddr" || type_lower == "ipaddr" ||
              type_lower == "opaque" || type_lower == "bitstring" || type_lower == "nsapaddress" ||
              type_lower == "traptype" || type_lower == "notiftype" || type_lower == "objgroup" ||
              type_lower == "notifgroup" || type_lower == "modid" || type_lower == "agentcap" ||
              type_lower == "modcomp" || type_lower == "null" || type_lower == "other") {
      return "No Conversion Available"; // For these types, we return "" to indicate no conversion
   }

   // Fallback for unknown types or specific cases not handled above
   return "Unknown Conversion";
}

std::string ResultBase::_to_string() const {
   return "oid: " + this->oid + ", index: " + this->index + ", type: " + this->type +
          ", value: " + this->value;
}

std::optional<int> ResultBase::_get_converted_value_int() const {
   if (std::holds_alternative<int>(converted_value)) {
      return std::get<int>(converted_value);
   }
   return std::nullopt;
}

std::optional<uint32_t> ResultBase::_get_converted_value_uint32() const {
   if (std::holds_alternative<uint32_t>(converted_value)) {
      return std::get<uint32_t>(converted_value);
   }
   return std::nullopt;
}

std::optional<uint64_t> ResultBase::_get_converted_value_uint64() const {
   if (std::holds_alternative<uint64_t>(converted_value)) {
      return std::get<uint64_t>(converted_value);
   }
   return std::nullopt;
}

std::optional<double> ResultBase::_get_converted_value_double() const {
   if (std::holds_alternative<double>(converted_value)) {
      return std::get<double>(converted_value);
   }
   return std::nullopt;
}

void ResultBase::update_converted_value() {
   this->converted_value = _make_converted_value(this->type, this->value);
}