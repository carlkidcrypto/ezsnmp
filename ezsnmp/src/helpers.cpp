/* straight copy from
 * https://github.com/net-snmp/net-snmp/blob/d5afe2e9e02def1c2d663828cd1e18108183d95e/snmplib/mib.c#L3456
 */
/* Slight modifications to return std::string instead of print to stdout */

#include "helpers.h"

#include <cstring>
#include <regex>
#include <sstream>

std::string print_variable_to_string(oid const *objid, size_t objidlen,
                                     netsnmp_variable_list const *variable) {
   u_char *buf = nullptr;
   size_t buf_len = 256, out_len = 0;

   if ((buf = static_cast<u_char *>(calloc(buf_len, 1))) == nullptr) {
      return "[TRUNCATED]";
   } else {
      if (sprint_realloc_variable(&buf, &buf_len, &out_len, 1, objid, objidlen, variable)) {
         // Construct the formatted string
         std::string result(reinterpret_cast<char *>(buf), out_len);
         SNMP_FREE(buf); // Free the allocated buffer
         return result;
      } else {
         // Construct the truncated string
         std::string truncated(reinterpret_cast<char *>(buf));
         SNMP_FREE(buf); // Free the allocated buffer
         return truncated + " [TRUNCATED]";
      }
   }
}

std::unique_ptr<char *[]> create_argv(std::vector<std::string> const &args, int &argc) {
   argc = args.size() + 1;
   std::unique_ptr<char *[]> argv(new char *[argc + 1]);

   argv[0] = const_cast<char *>("netsnmp");

   for (int i = 0; i < static_cast<int>(args.size()); ++i) {
      argv[i + 1] = const_cast<char *>(args[i].c_str());
   }
   argv[argc] = nullptr;

   return argv;
}

// This regular expression is used to extract the index from an OID
// We attempt to extract the index from an OID (e.g. sysDescr.0
// or .iso.org.dod.internet.mgmt.mib-2.system.sysContact.0)
std::regex const OID_INDEX_RE(R"((
        \.?\d+(?:\.\d+)*               # numeric OID
        |                              # or
        (?:\w+(?:[-:]*\w+)+)          # regular OID
        |                              # or
        (?:\.?iso(?:\.\w+[-:]*\w+)+)  # fully qualified OID
    )
    \.?(.*)                            # OID index
)");

// This regular expression takes something like 'SNMPv2::mib-2.17.7.1.4.3.1.2.300'
// and splits it into 'SNMPv2::mib-2' and '17.7.1.4.3.1.2.300'
std::regex const OID_INDEX_RE2(R"(^([^\.]+::[^\.]+)\.(.*)$)"); // Added regex

Result parse_result(std::string const &input) {
   Result result;
   std::stringstream ss(input);
   std::string temp;

   // Extract OID
   std::getline(ss, result.oid, '=');
   result.oid = result.oid.substr(0, result.oid.find_last_not_of(' ') + 1);

   // Extract OID index using regexes (matching Python logic)
   std::smatch first_match;
   std::smatch second_match;

   if (std::regex_match(result.oid, second_match, OID_INDEX_RE2)) {
      std::string temp_oid = second_match[1].str(); // Create temporary strings
      std::string temp_index = second_match[2].str();
      result.oid = std::move(temp_oid); // Move from temporary strings
      result.index = std::move(temp_index);
   } else if (std::regex_match(result.oid, first_match, OID_INDEX_RE)) {
      std::string temp_oid = first_match[1].str(); // Create temporary strings
      std::string temp_index = first_match[2].str();
      result.oid = std::move(temp_oid); // Move from temporary strings
      result.index = std::move(temp_index);

   } else if (result.oid == ".") {
      result.index = "";
   } else {
      // Default case if no matches are found
      result.index = "";
   }

   // Extract type
   std::getline(ss, temp, ':');
   result.type = temp.substr(temp.find_last_of(' ') + 1);

   // Extract value
   std::getline(ss, temp);
   result.value = temp.substr(1, temp.size());

   return result;
}

std::vector<Result> parse_results(std::vector<std::string> const &inputs) {
   std::vector<Result> results;
   for (auto const &input : inputs) {
      results.push_back(parse_result(input));
   }
   return results;
}