/* straight copy from https://github.com/net-snmp/net-snmp/blob/d5afe2e9e02def1c2d663828cd1e18108183d95e/snmplib/mib.c#L3456 */
/* Slight modifications to return std::string instead of print to stdout */

#include <cstring>
#include <sstream>

#include "helpers.h"

std::string print_variable_to_string(const oid *objid, size_t objidlen, const netsnmp_variable_list *variable)
{
   u_char *buf = nullptr;
   size_t buf_len = 256, out_len = 0;

   if ((buf = static_cast<u_char *>(calloc(buf_len, 1))) == nullptr)
   {
      return "[TRUNCATED]";
   }
   else
   {
      if (sprint_realloc_variable(&buf, &buf_len, &out_len, 1, objid, objidlen, variable))
      {
         // Construct the formatted string
         std::string result(reinterpret_cast<char *>(buf), out_len);
         SNMP_FREE(buf); // Free the allocated buffer
         return result;
      }
      else
      {
         // Construct the truncated string
         std::string truncated(reinterpret_cast<char *>(buf));
         SNMP_FREE(buf); // Free the allocated buffer
         return truncated + " [TRUNCATED]";
      }
   }
}

std::unique_ptr<char *[]> create_argv(const std::vector<std::string> &args, int &argc)
{
   argc = args.size() + 1;
   std::unique_ptr<char *[]> argv(new char *[argc + 1]);

   argv[0] = const_cast<char *>("netsnmp");

   for (int i = 0; i < static_cast<int>(args.size()); ++i)
   {
      argv[i + 1] = const_cast<char *>(args[i].c_str());
   }
   argv[argc] = nullptr;

   return argv;
}

Result parse_result(const std::string &input)
{
   Result result;
   std::stringstream ss(input);
   std::string temp;

   // Extract OID
   std::getline(ss, result.oid, '=');
   result.oid = result.oid.substr(0, result.oid.find_last_not_of(' ') + 1);

   // Extract type
   std::getline(ss, temp, ':');
   result.type = temp.substr(temp.find_last_of(' ') + 1);

   // Extract value
   std::getline(ss, temp);
   result.value = temp.substr(1, temp.size());

   return result;
}

std::vector<Result> parse_results(const std::vector<std::string> &inputs)
{
   std::vector<Result> results;
   for (const auto &input : inputs)
   {
      results.push_back(parse_result(input));
   }
   return results;
}