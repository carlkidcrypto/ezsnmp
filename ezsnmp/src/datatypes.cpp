#include "datatypes.h"

BaseResult::ConvertedValue BaseResult::make_converted_value(std::string const& type,
                                                            std::string const& value) {
   if (type == "INTEGER" || type == "INTEGER32") {
      return std::stoi(value);
   } else if (type == "UINTEGER" || type == "UNSIGNED32" || type == "GAUGE" || type == "COUNTER") {
      return static_cast<uint32_t>(std::stoul(value));
   } else if (type == "COUNTER64") {
      return static_cast<uint64_t>(std::stoull(value));
   } else if (type == "TIMETICKS") {
      // TIMETICKS are usually represented as (ticks) days:hours:minutes:seconds.tenths
      // We'll extract the numeric value inside the parentheses
      size_t start = value.find('(');
      size_t end = value.find(')');
      if (start != std::string::npos && end != std::string::npos && end > start + 1) {
         std::string ticks_str = value.substr(start + 1, end - start - 1);
         return static_cast<uint32_t>(std::stoul(ticks_str));
      }
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

std::string BaseResult::to_string() const {
   return "oid: " + this->oid + ", index: " + this->index + ", type: " + this->type +
          ", value: " + this->value;
}

int BaseResult::get_converted_value_int() const { return std::get<int>(converted_value); }

uint32_t BaseResult::get_converted_value_uint32() const {
   return std::get<uint32_t>(converted_value);
}

uint64_t BaseResult::get_converted_value_uint64() const {
   return std::get<uint64_t>(converted_value);
}

double BaseResult::get_converted_value_double() const { return std::get<double>(converted_value); }

std::string const& BaseResult::get_string() const { return std::get<std::string>(converted_value); }