/* straight copy from https://github.com/net-snmp/net-snmp/blob/d5afe2e9e02def1c2d663828cd1e18108183d95e/snmplib/mib.c#L3456 */
/* Slight modifications to return std::string instead of print to stdout */

#include <cstring>

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

// Default argv[0] to always be the program name. This simplifies what the
// call looks like in higher level languages like python.
void add_first_arg(int *argc, char ***argv)
{
   if (*argc > 0)
   {
      int new_argc = *argc + 1;
      char **new_argv = (char **)malloc((new_argc + 1) * sizeof(char *));

      new_argv[0] = (char *)("ezsnmp_swig");

      for (int i = 0; i < *argc; ++i)
      {
         new_argv[i + 1] = (*argv)[i];
      }

      // Null-terminate the array
      new_argv[new_argc] = NULL;

      // // Free the old argv array
      // for (int i = 0; i < *argc; ++i)
      // {
      //    free((*argv)[i]);
      // }
      // free(*argv);

      // Update argc and argv
      *argc = new_argc;
      *argv = new_argv;
   }
}

void add_last_arg(int *argc, std::unique_ptr<char*[]> &argv, std::string const &value_to_add)
{
   if (*argc > 0)
   {
      int new_argc = *argc + 1;
      auto new_argv = std::make_unique<char*[]>(new_argc + 1);

      // Copy the existing arguments
      for (int i = 0; i < *argc; ++i)
      {
         new_argv[i] = argv[i];
      }

      // Add the new argument
      new_argv[*argc] = new char[value_to_add.size() + 1];
      std::strcpy(new_argv[*argc], value_to_add.c_str());

      // Null-terminate the array
      new_argv[new_argc] = nullptr;

      // Update argc and argv
      *argc = new_argc;
      argv = std::move(new_argv);
   }
}