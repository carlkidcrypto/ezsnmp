#include "sessionbase.h"

#include <cassert>
#include <cstring>
#include <map>

#include "snmpbulkget.h"
#include "snmpbulkwalk.h"
#include "snmpget.h"
#include "snmpgetnext.h"
#include "snmpset.h"
#include "snmpwalk.h"

// Take all the SessionBase class inputs and map them to:
// OPTIONS:
//   -v 1|2c|3             specifies SNMP version to use
// SNMP Version 1 or 2c specific
//   -c COMMUNITY          set the community string
// SNMP Version 3 specific
//   -a PROTOCOL           set authentication protocol
//   (MD5|SHA|SHA-224|SHA-256|SHA-384|SHA-512) -A PASSPHRASE         set
//   authentication protocol pass phrase -e ENGINE-ID          set security
//   engine ID (e.g. 800000020109840301) -E ENGINE-ID          set context
//   engine ID (e.g. 800000020109840301) -l LEVEL              set security
//   level (noAuthNoPriv|authNoPriv|authPriv) -n CONTEXT            set context
//   name (e.g. bridge1) -u USER-NAME          set security name (e.g. bert) -x
//   PROTOCOL           set privacy protocol (DES|AES) -X PASSPHRASE         set
//   privacy protocol pass phrase -Z BOOTS,TIME         set destination engine
//   boots/time
// General communication options
//   -r RETRIES            set the number of retries
//   -t TIMEOUT            set the request timeout (in seconds)
std::map<std::string, std::string> cml_param_lookup = {{"version", "-v"},
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
                                                       {"retries", "-r"},
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
 * @param [in] auth_protocol Set authentication protocol
 *(MD5|SHA|SHA-224|SHA-256|SHA-384|SHA-512). Default ``.
 * @param [in] auth_passphrase Set authentication protocol pass phrase. Default
 *``.
 * @param [in] security_engine_id Set security engine ID (e.g.
 *800000020109840301). Default ``.
 * @param [in] context_engine_id Set context engine ID (e.g.
 *800000020109840301). Default ``.
 * @param [in] security_level Set security level
 *(noAuthNoPriv|authNoPriv|authPriv). Default ``.
 * @param [in] context Set context name (e.g. bridge1). Default ``.
 * @param [in] security_username Set security name (e.g. bert). Default ``.
 * @param [in] privacy_protocol Set privacy protocol (DES|AES). Default ``.
 * @param [in] privacy_passphrase Set privacy protocol pass phrase. Default ``.
 * @param [in] boots_time Set destination engine boots/time. Default ``.
 * @param [in] retries Set the number of retries. Default `3`.
 * @param [in] timeout Set the request timeout (in seconds). Default `1`.
 ******************************************************************************/
SessionBase::SessionBase(std::string hostname, std::string port_number, std::string version,
                         std::string community, std::string auth_protocol,
                         std::string auth_passphrase, std::string security_engine_id,
                         std::string context_engine_id, std::string security_level,
                         std::string context, std::string security_username,
                         std::string privacy_protocol, std::string privacy_passphrase,
                         std::string boots_time, std::string retries, std::string timeout)
    : m_hostname(hostname),
      m_port_number(port_number),
      m_version(version),
      m_community(community),
      m_auth_protocol(auth_protocol),
      m_auth_passphrase(auth_passphrase),
      m_security_engine_id(security_engine_id),
      m_context_engine_id(context_engine_id),
      m_security_level(security_level),
      m_context(context),
      m_security_username(security_username),
      m_privacy_protocol(privacy_protocol),
      m_privacy_passphrase(privacy_passphrase),
      m_boots_time(boots_time),
      m_retries(retries),
      m_timeout(timeout) {
   populate_args();
}

SessionBase::~SessionBase() {}

void SessionBase::populate_args() {
   m_args.clear();

   // Convert arguments to m_argc and m_argv
   std::map<std::string, std::string> input_arg_name_map = {
       {"hostname", m_hostname},
       {"port_number", m_port_number},
       {"version", m_version},
       {"community", m_community},
       {"auth_protocol", m_auth_protocol},
       {"auth_passphrase", m_auth_passphrase},
       {"security_engine_id", m_security_engine_id},
       {"context_engine_id", m_context_engine_id},
       {"security_level", m_security_level},
       {"context", m_context},
       {"security_username", m_security_username},
       {"privacy_protocol", m_privacy_protocol},
       {"privacy_passphrase", m_privacy_passphrase},
       {"boots_time", m_boots_time},
       {"retries", m_retries},
       {"timeout", m_timeout}};

   for (auto const& [key, val] : input_arg_name_map) {
      if (!val.empty() && key != "hostname" && key != "port_number") {
         // Copy the cml parameter flag i.e -a, -A, -x, etc...
         m_args.push_back(cml_param_lookup[key]);

         // Copy the input paramater value...
         m_args.push_back(val);
      }
   }

   // Add and make the host address
   // Note: We allow the hostname to contain the port number like `localhost:161` or
   // `[2001:db8::]:161`. If it is provided that way then port_number must be empty otherwise we
   // raise an error. We do this to maintain compatibility with what V1.X.X version do.
   auto host_address = std::string("");
   if (!input_arg_name_map["hostname"].empty()) {
      std::string hostname = input_arg_name_map["hostname"];
      std::string port_number = "";

      // Check for IPv6 address (enclosed in brackets)
      size_t openBracketPos = hostname.find('[');
      size_t closeBracketPos = hostname.find(']');
      if (openBracketPos != std::string::npos && closeBracketPos != std::string::npos) {
         // Extract the IPv6 address and port number
         hostname = hostname.substr(openBracketPos + 1, closeBracketPos - openBracketPos - 1);
         size_t colonPos = hostname.find(':', closeBracketPos);
         if (colonPos != std::string::npos) {
            port_number = hostname.substr(colonPos + 1);
            hostname = hostname.substr(0, colonPos);
         }
      } else {
         // IPv4 address or hostname
         size_t colonPos = hostname.find(':');
         if (colonPos != std::string::npos) {
            port_number = hostname.substr(colonPos + 1);
            hostname = hostname.substr(0, colonPos);
         }
      }

      // Now you have separate hostname and port_number
      input_arg_name_map["hostname"] = hostname;
      input_arg_name_map["port_number"] = port_number;
      m_hostname = hostname;
      m_port_number = port_number;

      // Construct the host_address as needed
      if (!port_number.empty()) {
         host_address = hostname + ":" + port_number;
      } else {
         host_address = hostname;
      }
   } else {
      host_address = "";
   }

   m_args.push_back(host_address);
}

std::vector<Result> SessionBase::walk(std::string mib) {
   populate_args();

   if (!mib.empty()) {
      m_args.push_back(mib);
   }

   return snmpwalk(m_args);
}

std::vector<Result> SessionBase::bulk_walk(std::vector<std::string> const& mibs) {
   populate_args();

   for (auto const& entry : mibs) {
      m_args.push_back(entry);
   }

   return snmpbulkwalk(m_args);
}

std::vector<Result> SessionBase::get(std::string mib) {
   populate_args();

   if (!mib.empty()) {
      m_args.push_back(mib);
   }

   return snmpget(m_args);
}

std::vector<Result> SessionBase::get_next(std::vector<std::string> const& mibs) {
   populate_args();

   for (auto const& entry : mibs) {
      m_args.push_back(entry);
   }

   return snmpgetnext(m_args);
}

std::vector<Result> SessionBase::bulk_get(std::vector<std::string> const& mibs) {
   populate_args();

   for (auto const& entry : mibs) {
      m_args.push_back(entry);
   }

   return snmpbulkget(m_args);
}

std::vector<Result> SessionBase::set(std::vector<std::string> const& mibs) {
   populate_args();

   for (auto const& entry : mibs) {
      m_args.push_back(entry);
   }

   return snmpset(m_args);
}

std::vector<std::string> const& SessionBase::_get_args() const { return m_args; }
std::string const& SessionBase::_get_hostname() const { return m_hostname; }
std::string const& SessionBase::_get_port_number() const { return m_port_number; }
std::string const& SessionBase::_get_version() const { return m_version; }
std::string const& SessionBase::_get_community() const { return m_community; }
std::string const& SessionBase::_get_auth_protocol() const { return m_auth_protocol; }
std::string const& SessionBase::_get_auth_passphrase() const { return m_auth_passphrase; }
std::string const& SessionBase::_get_security_engine_id() const { return m_security_engine_id; }
std::string const& SessionBase::_get_context_engine_id() const { return m_context_engine_id; }
std::string const& SessionBase::_get_security_level() const { return m_security_level; }
std::string const& SessionBase::_get_context() const { return m_context; }
std::string const& SessionBase::_get_security_username() const { return m_security_username; }
std::string const& SessionBase::_get_privacy_protocol() const { return m_privacy_protocol; }
std::string const& SessionBase::_get_privacy_passphrase() const { return m_privacy_passphrase; }
std::string const& SessionBase::_get_boots_time() const { return m_boots_time; }
std::string const& SessionBase::_get_retries() const { return m_retries; }
std::string const& SessionBase::_get_timeout() const { return m_timeout; }
void SessionBase::_set_hostname(std::string const& hostname) { m_hostname = hostname; }
void SessionBase::_set_port_number(std::string const& port_number) { m_port_number = port_number; }
void SessionBase::_set_version(std::string const& version) { m_version = version; }
void SessionBase::_set_community(std::string const& community) { m_community = community; }
void SessionBase::_set_auth_protocol(std::string const& auth_protocol) {
   m_auth_protocol = auth_protocol;
}
void SessionBase::_set_auth_passphrase(std::string const& auth_passphrase) {
   m_auth_passphrase = auth_passphrase;
}
void SessionBase::_set_security_engine_id(std::string const& security_engine_id) {
   m_security_engine_id = security_engine_id;
}
void SessionBase::_set_context_engine_id(std::string const& context_engine_id) {
   m_context_engine_id = context_engine_id;
}
void SessionBase::_set_security_level(std::string const& security_level) {
   m_security_level = security_level;
}
void SessionBase::_set_context(std::string const& context) { m_context = context; }
void SessionBase::_set_security_username(std::string const& security_username) {
   m_security_username = security_username;
}
void SessionBase::_set_privacy_protocol(std::string const& privacy_protocol) {
   m_privacy_protocol = privacy_protocol;
}
void SessionBase::_set_privacy_passphrase(std::string const& privacy_passphrase) {
   m_privacy_passphrase = privacy_passphrase;
}
void SessionBase::_set_boots_time(std::string const& boots_time) { m_boots_time = boots_time; }
void SessionBase::_set_retries(std::string const& retries) { m_retries = retries; }
void SessionBase::_set_timeout(std::string const& timeout) { m_timeout = timeout; }
