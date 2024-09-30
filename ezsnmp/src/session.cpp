#include <map>
#include <cstring>
#include <iostream>

#include "session.h"
#include "snmpwalk.h"
#include "snmpbulkwalk.h"
#include "snmpget.h"
#include "snmpbulkget.h"

// Take all the Session class inputs and map them to:
// OPTIONS:
//   -v 1|2c|3             specifies SNMP version to use
// SNMP Version 1 or 2c specific
//   -c COMMUNITY          set the community string
// SNMP Version 3 specific
//   -a PROTOCOL           set authentication protocol (MD5|SHA|SHA-224|SHA-256|SHA-384|SHA-512)
//   -A PASSPHRASE         set authentication protocol pass phrase
//   -e ENGINE-ID          set security engine ID (e.g. 800000020109840301)
//   -E ENGINE-ID          set context engine ID (e.g. 800000020109840301)
//   -l LEVEL              set security level (noAuthNoPriv|authNoPriv|authPriv)
//   -n CONTEXT            set context name (e.g. bridge1)
//   -u USER-NAME          set security name (e.g. bert)
//   -x PROTOCOL           set privacy protocol (DES|AES)
//   -X PASSPHRASE         set privacy protocol pass phrase
//   -Z BOOTS,TIME         set destination engine boots/time
// General communication options
//   -r RETRIES            set the number of retries
//   -t TIMEOUT            set the request timeout (in seconds)
std::map<std::string, std::string> cml_param_lookup = {
    {"version", "-v"},
    {"community", "-c"},
    {"auth_protocol", "-a"},
    {"auth_passphrase", "-A"},
    {"security_engine_id", "-e"},
    {"context_engine_id", "-E"},
    {"security_level", "-l"},
    {"context", "-n"},
    {"security_username", "-u"},
    {"privacy_protocol", "-x"},
    {"privacy_passphrase", "-X"},
    {"boots_time", "-Z"},
    {"retires", "-r"},
    {"timeout", "-t"}};

/******************************************************************************
 * The class constructor. This is a wrapper around the lower level c++ calls.
 * This allows for reuse of given parameters for multiple calls to functions
 * like: snmpwalk, snmpget, etc...
 *
 * @param [in] hostname
 * @param [in] port_number
 * @param [in] version 1|2c|3 specifies SNMP version to use. Default is `3`.
 * @param [in] community Set the community string. Default `public`
 * @param [in] auth_protocol Set authentication protocol (MD5|SHA|SHA-224|SHA-256|SHA-384|SHA-512). Default ``.
 * @param [in] auth_passphrase Set authentication protocol pass phrase. Default ``.
 * @param [in] security_engine_id Set security engine ID (e.g. 800000020109840301). Default ``.
 * @param [in] context_engine_id Set context engine ID (e.g. 800000020109840301). Default ``.
 * @param [in] security_level Set security level (noAuthNoPriv|authNoPriv|authPriv). Default ``.
 * @param [in] context Set context name (e.g. bridge1). Default ``.
 * @param [in] security_username Set security name (e.g. bert). Default ``.
 * @param [in] privacy_protocol Set privacy protocol (DES|AES). Default ``.
 * @param [in] privacy_passphrase Set privacy protocol pass phrase. Default ``.
 * @param [in] boots_time Set destination engine boots/time. Default ``.
 * @param [in] retires Set the number of retries. Default `3`.
 * @param [in] timeout Set the request timeout (in seconds). Default `1`.
 ******************************************************************************/
Session::Session(std::string hostname,
                 std::string port_number,
                 std::string version,
                 std::string community,
                 std::string auth_protocol,
                 std::string auth_passphrase,
                 std::string security_engine_id,
                 std::string context_engine_id,
                 std::string security_level,
                 std::string context,
                 std::string security_username,
                 std::string privacy_protocol,
                 std::string privacy_passphrase,
                 std::string boots_time,
                 std::string retires,
                 std::string timeout)

{
   // Convert arguments to m_argc and m_argv
   std::map<std::string, std::string> input_arg_name_map = {
       {"hostname", hostname},
       {"port_number", port_number},
       {"version", version},
       {"community", community},
       {"auth_protocol", auth_protocol},
       {"auth_passphrase", auth_passphrase},
       {"security_engine_id", security_engine_id},
       {"context_engine_id", context_engine_id},
       {"security_level", security_level},
       {"context", context},
       {"security_username", security_username},
       {"privacy_protocol", privacy_protocol},
       {"privacy_passphrase", privacy_passphrase},
       {"boots_time", boots_time},
       {"retires", retires},
       {"timeout", timeout}};

   m_argc = 0;
   m_argv = new char *[m_argc];

   auto host_address = std::string("");
   for (auto const &[key, val] : input_arg_name_map)
   {
      if (!val.empty() && (key != "hostname" || key != "port_number"))
      {
         // Copy the cml parameter flag i.e -a, -A, -x, etc...
         m_argv[m_argc] = new char[cml_param_lookup[key].size() + 1];
         std::strcpy(m_argv[m_argc], cml_param_lookup[key].c_str());
         m_argc++;

         // Copy the input paramater value...
         m_argv[m_argc] = new char[val.size() + 1];
         std::strcpy(m_argv[m_argc], val.c_str());
         m_argc++;
      }
      else if (!val.empty() && key == "hostname")
      {
         host_address = host_address + val;
      }
      else if (!val.empty() && key == "port_number")
      {
         host_address = host_address + ":" + val;
      }
   }

   // Now add the host address last...
   m_argv[m_argc] = new char[host_address.size() + 1];
   std::strcpy(m_argv[m_argc], host_address.c_str());

   std::cout << "m_argc: " << m_argc << std::endl;
   for (int i = 0; i < m_argc; ++i)
   {
      std::cout << "m_argv: " << &m_argv[m_argc] << std::endl;
   }
}

Session::~Session()
{
   for (int i = 0; i < m_argc; ++i)
   {
      delete[] m_argv[i];
   }
   delete[] m_argv;
}

std::vector<std::string> Session::walk()
{
   return snmpwalk(m_argc, m_argv);
}

std::vector<std::string> Session::bulk_walk()
{
   return snmpbulkwalk(m_argc, m_argv);
}

std::vector<std::string> Session::get()
{
   return snmpget(m_argc, m_argv);
}

std::vector<std::string> Session::bulk_get()
{
   return snmpbulkget(m_argc, m_argv);
}
