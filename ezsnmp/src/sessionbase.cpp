#include "sessionbase.h"

#include <algorithm>
#include <cassert>
#include <cstddef>
#include <cstring>
#include <map>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "exceptionsbase.h"
#include "helpers.h"
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
//   (MD5|SHA|SHA-224|SHA-256|SHA-384|SHA-512)
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
//
// General options
//   -m MIB[:...]          load given list of MIBs (ALL loads everything)
//   -M DIR[:...]          look in given list of directories for MIBs
//     (default:
//     $HOME/.snmp/mibs:/usr/share/snmp/mibs:/usr/share/snmp/mibs/iana:/usr/share/snmp/mibs/ietf)
//   -O OUTOPTS            Toggle various defaults controlling output display:
//                           e:  print enums numerically
//                           f:  print full OIDs on output
//                           n:  print OIDs numerically
//                           t:  print timeticks unparsed as numeric integers
//   -C APPOPTS            Set various application specific behaviours:
//                           r<NUM>:  set max-repeaters to <NUM>. Only applies to GETBULK PDUs.
static std::map<std::string, std::string> CML_PARAM_LOOKUP = {
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
    {"retries", "-r"},
    {"timeout", "-t"},
    {"load_mibs", "-m"},
    {"mib_directories", "-M"},
    {"print_enums_numerically", "-O e"},
    {"print_full_oids", "-O f"},
    {"print_oids_numerically", "-O n"},
    {"print_timeticks_numerically", "-O t"},
    {"set_max_repeaters_to_num", "-Cr"},
};

SessionBase::SessionBase(std::string const& hostname,
                         std::string const& port_number,
                         std::string const& version,
                         std::string const& community,
                         std::string const& auth_protocol,
                         std::string const& auth_passphrase,
                         std::string const& security_engine_id,
                         std::string const& context_engine_id,
                         std::string const& security_level,
                         std::string const& context,
                         std::string const& security_username,
                         std::string const& privacy_protocol,
                         std::string const& privacy_passphrase,
                         std::string const& boots_time,
                         std::string const& retries,
                         std::string const& timeout,
                         std::string const& load_mibs,
                         std::string const& mib_directories,
                         bool print_enums_numerically,
                         bool print_full_oids,
                         bool print_oids_numerically,
                         bool print_timeticks_numerically,
                         std::string const& set_max_repeaters_to_num)
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
      m_timeout(timeout),
      m_load_mibs(load_mibs),
      m_mib_directories(mib_directories),
      m_print_enums_numerically(print_enums_numerically),
      m_print_full_oids(print_full_oids),
      m_print_oids_numerically(print_oids_numerically),
      m_print_timeticks_numerically(print_timeticks_numerically),
      m_set_max_repeaters_to_num(set_max_repeaters_to_num) {
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
       {"timeout", m_timeout},
       {"load_mibs", m_load_mibs},
       {"mib_directories", m_mib_directories},
       {"set_max_repeaters_to_num", m_set_max_repeaters_to_num}};

   // Handle string parameters
   for (auto const& [key, val] : input_arg_name_map) {
      if (!val.empty() && key != "hostname" && key != "port_number") {
         // This one is different, it does not have a space between flag and value
         if (key == "set_max_repeaters_to_num") {
            m_args.push_back(CML_PARAM_LOOKUP[key] + val);
         } else {
            m_args.push_back(CML_PARAM_LOOKUP[key]);
            m_args.push_back(val);
         }
      }
   }

   // Helper function to split string by delimiter
   auto split_string = [](std::string const& str_in, char delimiter) -> std::vector<std::string> {
      std::vector<std::string> tokens;
      std::string token;
      std::istringstream tokenStream(str_in);
      while (std::getline(tokenStream, token, delimiter)) {
         tokens.push_back(token);
      }
      return tokens;
   };

   // Handle boolean parameters
   if (m_print_enums_numerically) {
      auto const& enum_parts = split_string(CML_PARAM_LOOKUP["print_enums_numerically"], ' ');
      auto const& option = enum_parts[0];
      auto const& value = enum_parts[1];
      m_args.push_back(option);
      m_args.push_back(value);
   }
   if (m_print_full_oids) {
      auto const& full_parts = split_string(CML_PARAM_LOOKUP["print_full_oids"], ' ');
      auto const& option = full_parts[0];
      auto const& value = full_parts[1];
      m_args.push_back(option);
      m_args.push_back(value);
   }
   if (m_print_oids_numerically) {
      auto const& num_parts = split_string(CML_PARAM_LOOKUP["print_oids_numerically"], ' ');
      auto const& option = num_parts[0];
      auto const& value = num_parts[1];
      m_args.push_back(option);
      m_args.push_back(value);
   }
   if (m_print_timeticks_numerically) {
      auto const& t_parts = split_string(CML_PARAM_LOOKUP["print_timeticks_numerically"], ' ');
      auto const& option = t_parts[0];
      auto const& value = t_parts[1];
      m_args.push_back(option);
      m_args.push_back(value);
   }

   // Add and make the host address
   // Note: We allow the hostname to contain the port number like `localhost:161`,
   // `udp6:[2001:db8::]`, or `[2001:db8::]:161`. If it is provided that way then
   // port_number must be empty otherwise we raise an error. We do this to maintain
   // compatibility with what V1.X.X version do.
   auto host_address = std::string("");
   if (!input_arg_name_map["hostname"].empty()) {
      std::string temp_hostname = input_arg_name_map["hostname"];
      std::string temp_port_number = "";

      // Check for `udp6` in something like this `udp6:[2001:db8::]`
      size_t IsUdp6InStr = temp_hostname.find("udp6");

      // Check for IPv6 address (enclosed in brackets)
      size_t openBracketPos = temp_hostname.find('[');
      size_t closeBracketPos = temp_hostname.find(']');

      // Check for `udp6:[2001:db8::]` or `udp6:[2001:db8::]:162`
      if (IsUdp6InStr != std::string::npos && openBracketPos != std::string::npos &&
          closeBracketPos != std::string::npos) {
         size_t lastColonPos = temp_hostname.find(':', closeBracketPos + 1);

         // Do a check if something like `udp6:[2001:db8::]:162` was provided
         if (lastColonPos != std::string::npos) {
            // Colon found after bracket, extract hostname and port
            temp_port_number = temp_hostname.substr(lastColonPos + 1);
            temp_hostname = temp_hostname.substr(0, closeBracketPos + 1);
         }

      }
      // Check for `[2001:db8::]:162`
      else if (IsUdp6InStr == std::string::npos && openBracketPos != std::string::npos &&
               closeBracketPos != std::string::npos) {
         // Extract the IPv6 address and port number
         std::string temp_split_hostname = "";
         std::string temp_split_port_number = "";
         temp_split_hostname =
             temp_hostname.substr(openBracketPos, (closeBracketPos + 1) - openBracketPos);
         size_t colonPos = temp_hostname.find(':', closeBracketPos);
         if (colonPos != std::string::npos) {
            temp_split_port_number = temp_hostname.substr(colonPos + 1);
            temp_split_hostname = temp_hostname.substr(0, colonPos);
         }

         // Assign temp splits back to temps
         temp_hostname = temp_split_hostname;
         temp_port_number = temp_split_port_number;

      } else {
         // Count the number of colons to determine if it's an IPv6 address
         int colonCount = std::count(temp_hostname.begin(), temp_hostname.end(), ':');
         if (colonCount >= 2) { // IPv6 addresses have at least 2 colons
                                // This is an IPv6 address without brackets
                                // No need to extract port here, it will be handled later
         } else {
            // IPv4 address or hostname
            size_t colonPos = temp_hostname.find(':');
            if (colonPos != std::string::npos) {
               temp_port_number = temp_hostname.substr(colonPos + 1);
               temp_hostname = temp_hostname.substr(0, colonPos);
            }
         }
      }

      // Now check that the port number wasn't provided both via hostname and port_number inputs
      // args
      if (!temp_port_number.empty() && !input_arg_name_map["port_number"].empty()) {
         throw ParseErrorBase(
             "Error: Provide either 'hostname' with port included (e.g., localhost:1234, "
             "[2001:db8::]:161, etc) or 'hostname' and 'port_number' separately, not both.");
      }

      // Now you have separate hostname and port_number
      input_arg_name_map["hostname"] = temp_hostname;
      m_hostname = temp_hostname;
      if (!temp_port_number.empty()) {
         input_arg_name_map["port_number"] = temp_port_number;
         m_port_number = temp_port_number;
      }

      // Construct the host_address as needed
      if (!input_arg_name_map["port_number"].empty()) {
         host_address = input_arg_name_map["hostname"] + ":" + input_arg_name_map["port_number"];
      } else {
         host_address = input_arg_name_map["hostname"];
      }
   } else {
      host_address = "";
   }

   m_args.push_back(host_address);
}

void SessionBase::check_and_clear_v3_user() {
   if (m_version == "3") {
      remove_v3_user_from_cache(m_security_username, m_context_engine_id);
   }
}

std::vector<Result> SessionBase::walk(std::string const& mib) {
   populate_args();

   if (!mib.empty()) {
      m_args.push_back(mib);
   }

   int rand_num = 1 + (std::rand() % 100000);
   std::string unique_init_snmp_name = "ezsnmp_walk_" + std::to_string(rand_num);
   return snmpwalk(m_args, unique_init_snmp_name);
}

std::vector<Result> SessionBase::bulk_walk(std::string const& mib) {
   populate_args();

   if (!mib.empty()) {
      m_args.push_back(mib);
   }

   int rand_num = 1 + (std::rand() % 100000);
   std::string unique_init_snmp_name = "ezsnmp_bulkwalk_" + std::to_string(rand_num);
   return snmpbulkwalk(m_args, unique_init_snmp_name);
}

std::vector<Result> SessionBase::bulk_walk(std::vector<std::string> const& mibs) {
   populate_args();

   for (auto const& entry : mibs) {
      m_args.push_back(entry);
   }

   int rand_num = 1 + (std::rand() % 100000);
   std::string unique_init_snmp_name = "ezsnmp_bulkwalk_" + std::to_string(rand_num);
   return snmpbulkwalk(m_args, unique_init_snmp_name);
}

std::vector<Result> SessionBase::get(std::string const& mib) {
   populate_args();

   if (!mib.empty()) {
      m_args.push_back(mib);
   }

   int rand_num = 1 + (std::rand() % 100000);
   std::string unique_init_snmp_name = "ezsnmp_get_" + std::to_string(rand_num);
   return snmpget(m_args, unique_init_snmp_name);
}

std::vector<Result> SessionBase::get(std::vector<std::string> const& mibs) {
   populate_args();

   for (auto const& entry : mibs) {
      m_args.push_back(entry);
   }

   int rand_num = 1 + (std::rand() % 100000);
   std::string unique_init_snmp_name = "ezsnmp_get_" + std::to_string(rand_num);
   return snmpget(m_args, unique_init_snmp_name);
}

std::vector<Result> SessionBase::get_next(std::vector<std::string> const& mibs) {
   populate_args();

   for (auto const& entry : mibs) {
      m_args.push_back(entry);
   }

   int rand_num = 1 + (std::rand() % 100000);
   std::string unique_init_snmp_name = "ezsnmp_getnext_" + std::to_string(rand_num);
   return snmpgetnext(m_args, unique_init_snmp_name);
}

std::vector<Result> SessionBase::bulk_get(std::vector<std::string> const& mibs) {
   populate_args();

   for (auto const& entry : mibs) {
      m_args.push_back(entry);
   }

   int rand_num = 1 + (std::rand() % 100000);
   std::string unique_init_snmp_name = "ezsnmp_bulkget_" + std::to_string(rand_num);
   return snmpbulkget(m_args, unique_init_snmp_name);
}

std::vector<Result> SessionBase::set(std::vector<std::string> const& mibs) {
   populate_args();

   for (auto const& entry : mibs) {
      m_args.push_back(entry);
   }

   int rand_num = 1 + (std::rand() % 100000);
   std::string unique_init_snmp_name = "ezsnmp_set_" + std::to_string(rand_num);
   return snmpset(m_args, unique_init_snmp_name);
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
void SessionBase::_set_hostname(std::string const& hostname) {
   m_hostname = hostname;
   populate_args();
}
void SessionBase::_set_port_number(std::string const& port_number) {
   m_port_number = port_number;
   populate_args();
}
void SessionBase::_set_version(std::string const& version) {
   m_version = version;
   populate_args();
}
void SessionBase::_set_community(std::string const& community) {
   m_community = community;
   populate_args();
}
void SessionBase::_set_auth_protocol(std::string const& auth_protocol) {
   m_auth_protocol = auth_protocol;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_auth_passphrase(std::string const& auth_passphrase) {
   m_auth_passphrase = auth_passphrase;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_security_engine_id(std::string const& security_engine_id) {
   m_security_engine_id = security_engine_id;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_context_engine_id(std::string const& context_engine_id) {
   m_context_engine_id = context_engine_id;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_security_level(std::string const& security_level) {
   m_security_level = security_level;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_context(std::string const& context) {
   m_context = context;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_security_username(std::string const& security_username) {
   m_security_username = security_username;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_privacy_protocol(std::string const& privacy_protocol) {
   m_privacy_protocol = privacy_protocol;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_privacy_passphrase(std::string const& privacy_passphrase) {
   m_privacy_passphrase = privacy_passphrase;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_boots_time(std::string const& boots_time) {
   m_boots_time = boots_time;
   populate_args();
}
void SessionBase::_set_retries(std::string const& retries) {
   m_retries = retries;
   populate_args();
}
void SessionBase::_set_timeout(std::string const& timeout) {
   m_timeout = timeout;
   populate_args();
}

void SessionBase::_set_load_mibs(std::string const& load_mibs) {
   m_load_mibs = load_mibs;
   populate_args();
}

void SessionBase::_set_mib_directories(std::string const& mib_directories) {
   m_mib_directories = mib_directories;
   populate_args();
}

void SessionBase::_set_print_enums_numerically(bool print_enums_numerically) {
   m_print_enums_numerically = print_enums_numerically;
   populate_args();
}

void SessionBase::_set_print_full_oids(bool print_full_oids) {
   m_print_full_oids = print_full_oids;
   populate_args();
}

void SessionBase::_set_print_oids_numerically(bool print_oids_numerically) {
   m_print_oids_numerically = print_oids_numerically;
   populate_args();
}

void SessionBase::_set_print_timeticks_numerically(bool print_timeticks_numerically) {
   m_print_timeticks_numerically = print_timeticks_numerically;
   populate_args();
}

void SessionBase::_set_max_repeaters_to_num(std::string const& set_max_repeaters_to_num) {
   m_set_max_repeaters_to_num = set_max_repeaters_to_num;
   populate_args();
}