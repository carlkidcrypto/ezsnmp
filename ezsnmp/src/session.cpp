#include "session.h"

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
 * @param [in] security_name Set security name (e.g. bert). Default ``.
 * @param [in] privacy_protocol Set privacy protocol (DES|AES). Default ``.
 * @param [in] privacy_passphrase Set privacy protocol pass phrase. Default ``.
 * @param [in] boots_time Set destination engine boots/time. Default ``.
 * @param [in] retires Set the number of retries. Default `3`.
 * @param [in] timeout Set the request timeout (in seconds). Default `1`.
 ******************************************************************************/
Session::Session(std::string hostname = "localhost",
                 std::string port_number = "",
                 std::string version = "3",
                 std::string community = "public",
                 std::string auth_protocol = "",
                 std::string auth_passphrase = "",
                 std::string security_engine_id = "",
                 std::string context_engine_id = "",
                 std::string security_level = "",
                 std::string context = "",
                 std::string security_name = "",
                 std::string privacy_protocol = "",
                 std::string privacy_passphrase = "",
                 std::string boots_time = "",
                 std::string retires = "3",
                 std::string timeout = "1")

{
   // Convert arguments to m_argc and m_argv
   std::vector<std::string> args = {
       hostname,
       port_number,
       version,
       community,
       auth_protocol,
       auth_passphrase,
       security_engine_id,
       context_engine_id,
       security_level,
       context,
       security_name,
       privacy_protocol,
       privacy_passphrase,
       boots_time,
       retires,
       timeout};

   m_argc = args.size();
   m_argv = new char *[m_argc];

   for (int i = 0; i < m_argc; ++i)
   {
      if (!args[i].empty())
      {
         m_argv[i] = new char[args[i].size() + 1];
         std::strcpy(m_argv[i], args[i].c_str());
      }
      else
      {
         m_argc--;
      }
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