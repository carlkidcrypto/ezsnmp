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