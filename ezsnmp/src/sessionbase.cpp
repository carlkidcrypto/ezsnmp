#include "sessionbase.h"

#include <algorithm>
#include <atomic>
#include <cassert>
#include <cctype>
#include <cstddef>
#include <cstring>
#include <map>
#include <mutex>
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
#include "thread_safety.h"

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
//                           x:  print OCTET STRING values in hex format
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
    {"print_hex_strings", "-O x"},
    {"set_max_repeaters_to_num", "-Cr"},
    {"print_oid_suffix_only", "-O s"},
    {"print_oid_module_name", "-O S"},
    {"print_oid_ucd_style", "-O u"},
    {"print_ascii_strings", "-O a"},
    {"print_leading_zero_hex", "-O 0"},
    {"print_hex_text", "-O T"},
    {"dont_breakdown_oids", "-O b"},
    {"escape_quotes_in_indexes", "-O E"},
    {"extended_index_format", "-O X"},
    {"dont_print_units", "-O U"},
    {"output_precision", "-Op"},
    {"regex_oid_matching", "-I b"},
    {"ignore_display_hints", "-I h"},
    {"dont_check_range", "-I r"},
    {"random_access_oid", "-I R"},
    {"read_ucd_style_oid", "-I u"},
    {"oid_suffix", "-Is"},
    {"oid_prefix", "-IS"},
    {"mib_allow_underline", "-P u"},
    {"mib_comment_to_eol", "-P c"},
    {"mib_replace_with_latest", "-P R"},
    {"non_repeaters", "-Cn"},
    {"walk_dont_check_lexicographic", "-Cc"},
    {"walk_include_requested", "-Ci"},
    {"walk_dont_get_requested", "-CI"},
    {"walk_end_oid", "-CE"},
    {"dont_fix_pdus", "-Cf"},
};

namespace {

// Mutex to serialize SNMPv3 operations and USM cache manipulation.
// Net-SNMP's USM user cache is shared and not thread-safe. Concurrent V3 operations
// or V3 setter mutations must serialize cache clearing before and after operations.
std::mutex g_snmp_v3_operation_mutex;

class SnmpV3OperationGuard {
  public:
   SnmpV3OperationGuard(bool clear_v3_user,
                        std::string const& security_name,
                        std::string const& context_engine_id)
       : m_clear_v3_user(clear_v3_user),
         m_security_name(security_name),
         m_context_engine_id(context_engine_id) {
      if (m_clear_v3_user) {
         m_lock = std::unique_lock<std::mutex>(g_snmp_v3_operation_mutex);
         remove_v3_user_from_cache(m_security_name, m_context_engine_id);
      }
   }

   ~SnmpV3OperationGuard() {
      if (m_clear_v3_user) {
         remove_v3_user_from_cache(m_security_name, m_context_engine_id);
      }
   }

   SnmpV3OperationGuard(SnmpV3OperationGuard const&) = delete;
   SnmpV3OperationGuard& operator=(SnmpV3OperationGuard const&) = delete;

  private:
   bool m_clear_v3_user;
   std::string const& m_security_name;
   std::string const& m_context_engine_id;
   std::unique_lock<std::mutex> m_lock;
};

class SnmpV3SetterGuard {
  public:
   explicit SnmpV3SetterGuard(bool enabled) {
      if (enabled) {
         m_lock = std::unique_lock<std::mutex>(g_snmp_v3_operation_mutex);
      }
   }

   SnmpV3SetterGuard(SnmpV3SetterGuard const&) = delete;
   SnmpV3SetterGuard& operator=(SnmpV3SetterGuard const&) = delete;

  private:
   std::unique_lock<std::mutex> m_lock;
};

SessionFormattingOptions make_formatting_options(bool print_enums_numerically,
                                                 bool print_full_oids,
                                                 bool print_oids_numerically,
                                                 bool print_timeticks_numerically,
                                                 bool print_hex_strings,
                                                 bool print_oid_suffix_only,
                                                 bool print_oid_module_name,
                                                 bool print_oid_ucd_style,
                                                 bool print_ascii_strings,
                                                 bool print_leading_zero_hex,
                                                 bool print_hex_text,
                                                 bool dont_breakdown_oids,
                                                 bool escape_quotes_in_indexes,
                                                 bool extended_index_format,
                                                 bool dont_print_units,
                                                 std::string const& output_precision) {
   SessionFormattingOptions opts;
   opts.is_set = true;
   opts.print_enums_numerically = print_enums_numerically;
   opts.print_full_oids = print_full_oids;
   opts.print_oids_numerically = print_oids_numerically;
   opts.print_timeticks_numerically = print_timeticks_numerically;
   opts.print_hex_strings = print_hex_strings;
   opts.print_oid_suffix_only = print_oid_suffix_only;
   opts.print_oid_module_name = print_oid_module_name;
   opts.print_oid_ucd_style = print_oid_ucd_style;
   opts.print_ascii_strings = print_ascii_strings;
   opts.print_leading_zero_hex = print_leading_zero_hex;
   opts.print_hex_text = print_hex_text;
   opts.dont_breakdown_oids = dont_breakdown_oids;
   opts.escape_quotes_in_indexes = escape_quotes_in_indexes;
   opts.extended_index_format = extended_index_format;
   opts.dont_print_units = dont_print_units;
   opts.output_precision = output_precision;
   return opts;
}

} // namespace

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
                         bool print_hex_strings,
                         std::string const& set_max_repeaters_to_num,
                         bool print_oid_suffix_only,
                         bool print_oid_module_name,
                         bool print_oid_ucd_style,
                         bool print_ascii_strings,
                         bool print_leading_zero_hex,
                         bool print_hex_text,
                         bool dont_breakdown_oids,
                         bool escape_quotes_in_indexes,
                         bool extended_index_format,
                         bool dont_print_units,
                         std::string const& output_precision,
                         bool regex_oid_matching,
                         bool ignore_display_hints,
                         bool dont_check_range,
                         bool random_access_oid,
                         bool read_ucd_style_oid,
                         std::string const& oid_suffix,
                         std::string const& oid_prefix,
                         bool mib_allow_underline,
                         bool mib_comment_to_eol,
                         bool mib_replace_with_latest,
                         std::string const& non_repeaters,
                         bool walk_dont_check_lexicographic,
                         bool walk_include_requested,
                         bool walk_dont_get_requested,
                         std::string const& walk_end_oid,
                         bool dont_fix_pdus)
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
      m_print_hex_strings(print_hex_strings),
      m_set_max_repeaters_to_num(set_max_repeaters_to_num),
      m_print_oid_suffix_only(print_oid_suffix_only),
      m_print_oid_module_name(print_oid_module_name),
      m_print_oid_ucd_style(print_oid_ucd_style),
      m_print_ascii_strings(print_ascii_strings),
      m_print_leading_zero_hex(print_leading_zero_hex),
      m_print_hex_text(print_hex_text),
      m_dont_breakdown_oids(dont_breakdown_oids),
      m_escape_quotes_in_indexes(escape_quotes_in_indexes),
      m_extended_index_format(extended_index_format),
      m_dont_print_units(dont_print_units),
      m_output_precision(output_precision),
      m_regex_oid_matching(regex_oid_matching),
      m_ignore_display_hints(ignore_display_hints),
      m_dont_check_range(dont_check_range),
      m_random_access_oid(random_access_oid),
      m_read_ucd_style_oid(read_ucd_style_oid),
      m_oid_suffix(oid_suffix),
      m_oid_prefix(oid_prefix),
      m_mib_allow_underline(mib_allow_underline),
      m_mib_comment_to_eol(mib_comment_to_eol),
      m_mib_replace_with_latest(mib_replace_with_latest),
      m_non_repeaters(non_repeaters),
      m_walk_dont_check_lexicographic(walk_dont_check_lexicographic),
      m_walk_include_requested(walk_include_requested),
      m_walk_dont_get_requested(walk_dont_get_requested),
      m_walk_end_oid(walk_end_oid),
      m_dont_fix_pdus(dont_fix_pdus) {
   init_session();
}

namespace {
bool parse_bool_option(std::string const& key, std::string const& value) {
   std::string lower;
   lower.reserve(value.size());
   for (unsigned char ch : value) {
      lower.push_back(static_cast<char>(std::tolower(ch)));
   }
   if (lower == "true" || lower == "1" || lower == "yes") {
      return true;
   }
   if (lower == "false" || lower == "0" || lower == "no") {
      return false;
   }
   throw std::invalid_argument("Invalid boolean value '" + value + "' for option '" + key + "'");
}

void apply_option_map(std::map<std::string, std::string> const& options,
                      std::map<std::string, std::string*> const& string_fields,
                      std::map<std::string, bool*> const& bool_fields,
                      std::string const& group_name) {
   for (auto const& [key, value] : options) {
      if (auto it = string_fields.find(key); it != string_fields.end()) {
         *(it->second) = value;
      } else if (auto bit = bool_fields.find(key); bit != bool_fields.end()) {
         *(bit->second) = parse_bool_option(key, value);
      } else {
         throw std::invalid_argument("Unknown option '" + key + "' in " + group_name);
      }
   }
}
} // namespace

void SessionBase::init_session() {
   populate_args();

   static std::atomic<uint64_t> s_session_counter{1};
   m_init_name = "ezsnmp_" + std::to_string(s_session_counter.fetch_add(1));
}

void SessionBase::apply_connection_options(std::map<std::string, std::string> const& options) {
   apply_option_map(options,
                    {{"hostname", &m_hostname},
                     {"port_number", &m_port_number},
                     {"version", &m_version},
                     {"community", &m_community},
                     {"retries", &m_retries},
                     {"timeout", &m_timeout}},
                    {}, "connection_options");
}

void SessionBase::apply_v3_options(std::map<std::string, std::string> const& options) {
   apply_option_map(options,
                    {{"auth_protocol", &m_auth_protocol},
                     {"auth_passphrase", &m_auth_passphrase},
                     {"security_engine_id", &m_security_engine_id},
                     {"context_engine_id", &m_context_engine_id},
                     {"security_level", &m_security_level},
                     {"context", &m_context},
                     {"security_username", &m_security_username},
                     {"privacy_protocol", &m_privacy_protocol},
                     {"privacy_passphrase", &m_privacy_passphrase},
                     {"boots_time", &m_boots_time}},
                    {}, "v3_options");
}

void SessionBase::apply_mib_and_output_options(std::map<std::string, std::string> const& options) {
   apply_option_map(options,
                    {{"load_mibs", &m_load_mibs},
                     {"mib_directories", &m_mib_directories},
                     {"output_precision", &m_output_precision},
                     {"oid_suffix", &m_oid_suffix},
                     {"oid_prefix", &m_oid_prefix}},
                    {{"print_enums_numerically", &m_print_enums_numerically},
                     {"print_full_oids", &m_print_full_oids},
                     {"print_oids_numerically", &m_print_oids_numerically},
                     {"print_timeticks_numerically", &m_print_timeticks_numerically},
                     {"print_hex_strings", &m_print_hex_strings},
                     {"print_oid_suffix_only", &m_print_oid_suffix_only},
                     {"print_oid_module_name", &m_print_oid_module_name},
                     {"print_oid_ucd_style", &m_print_oid_ucd_style},
                     {"print_ascii_strings", &m_print_ascii_strings},
                     {"print_leading_zero_hex", &m_print_leading_zero_hex},
                     {"print_hex_text", &m_print_hex_text},
                     {"dont_breakdown_oids", &m_dont_breakdown_oids},
                     {"escape_quotes_in_indexes", &m_escape_quotes_in_indexes},
                     {"extended_index_format", &m_extended_index_format},
                     {"dont_print_units", &m_dont_print_units},
                     {"regex_oid_matching", &m_regex_oid_matching},
                     {"ignore_display_hints", &m_ignore_display_hints},
                     {"dont_check_range", &m_dont_check_range},
                     {"random_access_oid", &m_random_access_oid},
                     {"read_ucd_style_oid", &m_read_ucd_style_oid},
                     {"mib_allow_underline", &m_mib_allow_underline},
                     {"mib_comment_to_eol", &m_mib_comment_to_eol},
                     {"mib_replace_with_latest", &m_mib_replace_with_latest}},
                    "mib_and_output_options");
}

void SessionBase::apply_operation_options(std::map<std::string, std::string> const& options) {
   apply_option_map(options,
                    {{"set_max_repeaters_to_num", &m_set_max_repeaters_to_num},
                     {"non_repeaters", &m_non_repeaters},
                     {"walk_end_oid", &m_walk_end_oid}},
                    {{"walk_dont_check_lexicographic", &m_walk_dont_check_lexicographic},
                     {"walk_include_requested", &m_walk_include_requested},
                     {"walk_dont_get_requested", &m_walk_dont_get_requested},
                     {"dont_fix_pdus", &m_dont_fix_pdus}},
                    "operation_options");
}

SessionBase::SessionBase(std::map<std::string, std::string> const& connection_options,
                         std::map<std::string, std::string> const& v3_options,
                         std::map<std::string, std::string> const& mib_and_output_options,
                         std::map<std::string, std::string> const& operation_options) {
   apply_connection_options(connection_options);
   apply_v3_options(v3_options);
   apply_mib_and_output_options(mib_and_output_options);
   apply_operation_options(operation_options);
   init_session();
}

SessionBase::~SessionBase() {}

void SessionBase::_close() {
   // Reference-counted cleanup: only last thread calls snmp_shutdown()
   // snmp_shutdown() is called internally by netsnmp_thread_cleanup() when reference count reaches
   // 0
   netsnmp_thread_cleanup(m_init_name);
}

void SessionBase::populate_args(SnmpOperation op) {
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
   };

   // Handle string parameters
   for (auto const& [key, val] : input_arg_name_map) {
      if (!val.empty() && key != "hostname" && key != "port_number") {
         // Skip community for SNMPv3 (v3 uses security username, not community)
         if (key == "community" && m_version == "3") {
            continue;
         }
         m_args.push_back(CML_PARAM_LOOKUP[key]);
         m_args.push_back(val);
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

   auto append_bool_flags = [&](auto const& flags) {
      for (auto const& [enabled, key] : flags) {
         if (enabled) {
            auto const parts = split_string(CML_PARAM_LOOKUP[key], ' ');
            m_args.push_back(parts[0]);
            m_args.push_back(parts[1]);
         }
      }
   };

   // Handle -O output options
   std::pair<bool, char const*> const output_bool_flags[] = {
       {m_print_enums_numerically, "print_enums_numerically"},
       {m_print_full_oids, "print_full_oids"},
       {m_print_oids_numerically, "print_oids_numerically"},
       {m_print_timeticks_numerically, "print_timeticks_numerically"},
       {m_print_hex_strings, "print_hex_strings"},
       {m_print_oid_suffix_only, "print_oid_suffix_only"},
       {m_print_oid_module_name, "print_oid_module_name"},
       {m_print_oid_ucd_style, "print_oid_ucd_style"},
       {m_print_ascii_strings, "print_ascii_strings"},
       {m_print_leading_zero_hex, "print_leading_zero_hex"},
       {m_print_hex_text, "print_hex_text"},
       {m_dont_breakdown_oids, "dont_breakdown_oids"},
       {m_escape_quotes_in_indexes, "escape_quotes_in_indexes"},
       {m_extended_index_format, "extended_index_format"},
       {m_dont_print_units, "dont_print_units"},
   };
   append_bool_flags(output_bool_flags);
   if (!m_output_precision.empty()) {
      m_args.push_back(CML_PARAM_LOOKUP["output_precision"]);
      m_args.push_back(m_output_precision);
   }

   // Handle -I input options
   std::pair<bool, char const*> const input_bool_flags[] = {
       {m_regex_oid_matching, "regex_oid_matching"},
       {m_ignore_display_hints, "ignore_display_hints"},
       {m_dont_check_range, "dont_check_range"},
       {m_random_access_oid, "random_access_oid"},
       {m_read_ucd_style_oid, "read_ucd_style_oid"},
   };
   append_bool_flags(input_bool_flags);
   if (!m_oid_suffix.empty()) {
      m_args.push_back(CML_PARAM_LOOKUP["oid_suffix"]);
      m_args.push_back(m_oid_suffix);
   }
   if (!m_oid_prefix.empty()) {
      m_args.push_back(CML_PARAM_LOOKUP["oid_prefix"]);
      m_args.push_back(m_oid_prefix);
   }

   // Handle -P MIB parser options
   std::pair<bool, char const*> const mib_bool_flags[] = {
       {m_mib_allow_underline, "mib_allow_underline"},
       {m_mib_comment_to_eol, "mib_comment_to_eol"},
       {m_mib_replace_with_latest, "mib_replace_with_latest"},
   };
   append_bool_flags(mib_bool_flags);

   // Handle operation-scoped -C application options before host_address.
   // *_optProc throws ParseErrorBase on unsupported -C flags, so each operation
   // only receives the -C flags it supports.
   bool const is_all = (op == SnmpOperation::All);
   bool const is_bulk = (is_all || op == SnmpOperation::BulkGet || op == SnmpOperation::BulkWalk);
   bool const is_walk_or_bulk =
       (is_all || op == SnmpOperation::Walk || op == SnmpOperation::BulkWalk);
   bool const is_walk_only = (is_all || op == SnmpOperation::Walk);
   bool const is_get_or_next = (is_all || op == SnmpOperation::Get || op == SnmpOperation::GetNext);

   if (is_bulk && !m_set_max_repeaters_to_num.empty()) {
      m_args.push_back(CML_PARAM_LOOKUP["set_max_repeaters_to_num"] + m_set_max_repeaters_to_num);
   }
   if (is_bulk && !m_non_repeaters.empty()) {
      m_args.push_back(CML_PARAM_LOOKUP["non_repeaters"] + m_non_repeaters);
   }
   if (is_walk_or_bulk && m_walk_dont_check_lexicographic) {
      m_args.push_back(CML_PARAM_LOOKUP["walk_dont_check_lexicographic"]);
   }
   if (is_walk_or_bulk && m_walk_include_requested) {
      m_args.push_back(CML_PARAM_LOOKUP["walk_include_requested"]);
   }
   if (is_walk_only && m_walk_dont_get_requested) {
      m_args.push_back(CML_PARAM_LOOKUP["walk_dont_get_requested"]);
   }
   if (is_walk_only && !m_walk_end_oid.empty()) {
      m_args.push_back(CML_PARAM_LOOKUP["walk_end_oid"]);
      m_args.push_back(m_walk_end_oid);
   }
   if (is_get_or_next && m_dont_fix_pdus) {
      m_args.push_back(CML_PARAM_LOOKUP["dont_fix_pdus"]);
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
   FormattingScope fmt_guard(make_formatting_options(
       m_print_enums_numerically, m_print_full_oids, m_print_oids_numerically,
       m_print_timeticks_numerically, m_print_hex_strings, m_print_oid_suffix_only,
       m_print_oid_module_name, m_print_oid_ucd_style, m_print_ascii_strings,
       m_print_leading_zero_hex, m_print_hex_text, m_dont_breakdown_oids,
       m_escape_quotes_in_indexes, m_extended_index_format, m_dont_print_units,
       m_output_precision));
   SnmpV3OperationGuard v3_guard(m_version == "3", m_security_username, m_context_engine_id);
   populate_args(SnmpOperation::Walk);

   if (!mib.empty()) {
      m_args.push_back(mib);
   }

   return snmpwalk(m_args, m_init_name);
}

std::vector<Result> SessionBase::bulk_walk(std::string const& mib) {
   FormattingScope fmt_guard(make_formatting_options(
       m_print_enums_numerically, m_print_full_oids, m_print_oids_numerically,
       m_print_timeticks_numerically, m_print_hex_strings, m_print_oid_suffix_only,
       m_print_oid_module_name, m_print_oid_ucd_style, m_print_ascii_strings,
       m_print_leading_zero_hex, m_print_hex_text, m_dont_breakdown_oids,
       m_escape_quotes_in_indexes, m_extended_index_format, m_dont_print_units,
       m_output_precision));
   SnmpV3OperationGuard v3_guard(m_version == "3", m_security_username, m_context_engine_id);
   populate_args(SnmpOperation::BulkWalk);

   if (!mib.empty()) {
      m_args.push_back(mib);
   }

   return snmpbulkwalk(m_args, m_init_name);
}

std::vector<Result> SessionBase::bulk_walk(std::vector<std::string> const& mibs) {
   FormattingScope fmt_guard(make_formatting_options(
       m_print_enums_numerically, m_print_full_oids, m_print_oids_numerically,
       m_print_timeticks_numerically, m_print_hex_strings, m_print_oid_suffix_only,
       m_print_oid_module_name, m_print_oid_ucd_style, m_print_ascii_strings,
       m_print_leading_zero_hex, m_print_hex_text, m_dont_breakdown_oids,
       m_escape_quotes_in_indexes, m_extended_index_format, m_dont_print_units,
       m_output_precision));
   SnmpV3OperationGuard v3_guard(m_version == "3", m_security_username, m_context_engine_id);
   populate_args(SnmpOperation::BulkWalk);

   for (auto const& entry : mibs) {
      m_args.push_back(entry);
   }

   return snmpbulkwalk(m_args, m_init_name);
}

std::vector<Result> SessionBase::get(std::string const& mib) {
   FormattingScope fmt_guard(make_formatting_options(
       m_print_enums_numerically, m_print_full_oids, m_print_oids_numerically,
       m_print_timeticks_numerically, m_print_hex_strings, m_print_oid_suffix_only,
       m_print_oid_module_name, m_print_oid_ucd_style, m_print_ascii_strings,
       m_print_leading_zero_hex, m_print_hex_text, m_dont_breakdown_oids,
       m_escape_quotes_in_indexes, m_extended_index_format, m_dont_print_units,
       m_output_precision));
   SnmpV3OperationGuard v3_guard(m_version == "3", m_security_username, m_context_engine_id);
   populate_args(SnmpOperation::Get);

   if (!mib.empty()) {
      m_args.push_back(mib);
   }

   return snmpget(m_args, m_init_name);
}

std::vector<Result> SessionBase::get(std::vector<std::string> const& mibs) {
   FormattingScope fmt_guard(make_formatting_options(
       m_print_enums_numerically, m_print_full_oids, m_print_oids_numerically,
       m_print_timeticks_numerically, m_print_hex_strings, m_print_oid_suffix_only,
       m_print_oid_module_name, m_print_oid_ucd_style, m_print_ascii_strings,
       m_print_leading_zero_hex, m_print_hex_text, m_dont_breakdown_oids,
       m_escape_quotes_in_indexes, m_extended_index_format, m_dont_print_units,
       m_output_precision));
   SnmpV3OperationGuard v3_guard(m_version == "3", m_security_username, m_context_engine_id);
   populate_args(SnmpOperation::Get);

   for (auto const& entry : mibs) {
      m_args.push_back(entry);
   }

   return snmpget(m_args, m_init_name);
}

std::vector<Result> SessionBase::get_next(std::vector<std::string> const& mibs) {
   FormattingScope fmt_guard(make_formatting_options(
       m_print_enums_numerically, m_print_full_oids, m_print_oids_numerically,
       m_print_timeticks_numerically, m_print_hex_strings, m_print_oid_suffix_only,
       m_print_oid_module_name, m_print_oid_ucd_style, m_print_ascii_strings,
       m_print_leading_zero_hex, m_print_hex_text, m_dont_breakdown_oids,
       m_escape_quotes_in_indexes, m_extended_index_format, m_dont_print_units,
       m_output_precision));
   SnmpV3OperationGuard v3_guard(m_version == "3", m_security_username, m_context_engine_id);
   populate_args(SnmpOperation::GetNext);

   for (auto const& entry : mibs) {
      m_args.push_back(entry);
   }

   return snmpgetnext(m_args, m_init_name);
}

std::vector<Result> SessionBase::get_next(std::string const& mib) {
   std::vector<std::string> mibs;
   if (!mib.empty()) {
      mibs.push_back(mib);
   }
   return get_next(mibs);
}

std::vector<Result> SessionBase::bulk_get(std::string const& mib) {
   std::vector<std::string> mibs;
   if (!mib.empty()) {
      mibs.push_back(mib);
   }
   return bulk_get(mibs);
}

std::vector<Result> SessionBase::bulk_get(std::vector<std::string> const& mibs) {
   FormattingScope fmt_guard(make_formatting_options(
       m_print_enums_numerically, m_print_full_oids, m_print_oids_numerically,
       m_print_timeticks_numerically, m_print_hex_strings, m_print_oid_suffix_only,
       m_print_oid_module_name, m_print_oid_ucd_style, m_print_ascii_strings,
       m_print_leading_zero_hex, m_print_hex_text, m_dont_breakdown_oids,
       m_escape_quotes_in_indexes, m_extended_index_format, m_dont_print_units,
       m_output_precision));
   SnmpV3OperationGuard v3_guard(m_version == "3", m_security_username, m_context_engine_id);
   populate_args(SnmpOperation::BulkGet);

   for (auto const& entry : mibs) {
      m_args.push_back(entry);
   }

   return snmpbulkget(m_args, m_init_name);
}

std::vector<Result> SessionBase::set(std::vector<std::string> const& mibs) {
   FormattingScope fmt_guard(make_formatting_options(
       m_print_enums_numerically, m_print_full_oids, m_print_oids_numerically,
       m_print_timeticks_numerically, m_print_hex_strings, m_print_oid_suffix_only,
       m_print_oid_module_name, m_print_oid_ucd_style, m_print_ascii_strings,
       m_print_leading_zero_hex, m_print_hex_text, m_dont_breakdown_oids,
       m_escape_quotes_in_indexes, m_extended_index_format, m_dont_print_units,
       m_output_precision));
   SnmpV3OperationGuard v3_guard(m_version == "3", m_security_username, m_context_engine_id);
   populate_args(SnmpOperation::Set);

   for (auto const& entry : mibs) {
      m_args.push_back(entry);
   }

   return snmpset(m_args, m_init_name);
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
std::string const& SessionBase::_get_load_mibs() const { return m_load_mibs; }
std::string const& SessionBase::_get_mib_directories() const { return m_mib_directories; }
bool SessionBase::_get_print_enums_numerically() const { return m_print_enums_numerically; }
bool SessionBase::_get_print_full_oids() const { return m_print_full_oids; }
bool SessionBase::_get_print_oids_numerically() const { return m_print_oids_numerically; }
bool SessionBase::_get_print_timeticks_numerically() const { return m_print_timeticks_numerically; }
bool SessionBase::_get_print_hex_strings() const { return m_print_hex_strings; }
std::string const& SessionBase::_get_set_max_repeaters_to_num() const {
   return m_set_max_repeaters_to_num;
}
bool SessionBase::_get_print_oid_suffix_only() const { return m_print_oid_suffix_only; }
bool SessionBase::_get_print_oid_module_name() const { return m_print_oid_module_name; }
bool SessionBase::_get_print_oid_ucd_style() const { return m_print_oid_ucd_style; }
bool SessionBase::_get_print_ascii_strings() const { return m_print_ascii_strings; }
bool SessionBase::_get_print_leading_zero_hex() const { return m_print_leading_zero_hex; }
bool SessionBase::_get_print_hex_text() const { return m_print_hex_text; }
bool SessionBase::_get_dont_breakdown_oids() const { return m_dont_breakdown_oids; }
bool SessionBase::_get_escape_quotes_in_indexes() const { return m_escape_quotes_in_indexes; }
bool SessionBase::_get_extended_index_format() const { return m_extended_index_format; }
bool SessionBase::_get_dont_print_units() const { return m_dont_print_units; }
std::string const& SessionBase::_get_output_precision() const { return m_output_precision; }
bool SessionBase::_get_regex_oid_matching() const { return m_regex_oid_matching; }
bool SessionBase::_get_ignore_display_hints() const { return m_ignore_display_hints; }
bool SessionBase::_get_dont_check_range() const { return m_dont_check_range; }
bool SessionBase::_get_random_access_oid() const { return m_random_access_oid; }
bool SessionBase::_get_read_ucd_style_oid() const { return m_read_ucd_style_oid; }
std::string const& SessionBase::_get_oid_suffix() const { return m_oid_suffix; }
std::string const& SessionBase::_get_oid_prefix() const { return m_oid_prefix; }
bool SessionBase::_get_mib_allow_underline() const { return m_mib_allow_underline; }
bool SessionBase::_get_mib_comment_to_eol() const { return m_mib_comment_to_eol; }
bool SessionBase::_get_mib_replace_with_latest() const { return m_mib_replace_with_latest; }
std::string const& SessionBase::_get_non_repeaters() const { return m_non_repeaters; }
bool SessionBase::_get_walk_dont_check_lexicographic() const {
   return m_walk_dont_check_lexicographic;
}
bool SessionBase::_get_walk_include_requested() const { return m_walk_include_requested; }
bool SessionBase::_get_walk_dont_get_requested() const { return m_walk_dont_get_requested; }
std::string const& SessionBase::_get_walk_end_oid() const { return m_walk_end_oid; }
bool SessionBase::_get_dont_fix_pdus() const { return m_dont_fix_pdus; }
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
   SnmpV3SetterGuard guard(m_version == "3");
   m_auth_protocol = auth_protocol;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_auth_passphrase(std::string const& auth_passphrase) {
   SnmpV3SetterGuard guard(m_version == "3");
   m_auth_passphrase = auth_passphrase;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_security_engine_id(std::string const& security_engine_id) {
   SnmpV3SetterGuard guard(m_version == "3");
   m_security_engine_id = security_engine_id;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_context_engine_id(std::string const& context_engine_id) {
   SnmpV3SetterGuard guard(m_version == "3");
   m_context_engine_id = context_engine_id;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_security_level(std::string const& security_level) {
   SnmpV3SetterGuard guard(m_version == "3");
   m_security_level = security_level;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_context(std::string const& context) {
   SnmpV3SetterGuard guard(m_version == "3");
   m_context = context;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_security_username(std::string const& security_username) {
   SnmpV3SetterGuard guard(m_version == "3");
   m_security_username = security_username;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_privacy_protocol(std::string const& privacy_protocol) {
   SnmpV3SetterGuard guard(m_version == "3");
   m_privacy_protocol = privacy_protocol;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_privacy_passphrase(std::string const& privacy_passphrase) {
   SnmpV3SetterGuard guard(m_version == "3");
   m_privacy_passphrase = privacy_passphrase;
   populate_args();
   check_and_clear_v3_user();
}
void SessionBase::_set_boots_time(std::string const& boots_time) {
   SnmpV3SetterGuard guard(m_version == "3");
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

void SessionBase::_set_print_hex_strings(bool print_hex_strings) {
   m_print_hex_strings = print_hex_strings;
   populate_args();
}

void SessionBase::_set_max_repeaters_to_num(std::string const& set_max_repeaters_to_num) {
   m_set_max_repeaters_to_num = set_max_repeaters_to_num;
   populate_args();
}

void SessionBase::_set_print_oid_suffix_only(bool print_oid_suffix_only) {
   m_print_oid_suffix_only = print_oid_suffix_only;
   populate_args();
}

void SessionBase::_set_print_oid_module_name(bool print_oid_module_name) {
   m_print_oid_module_name = print_oid_module_name;
   populate_args();
}

void SessionBase::_set_print_oid_ucd_style(bool print_oid_ucd_style) {
   m_print_oid_ucd_style = print_oid_ucd_style;
   populate_args();
}

void SessionBase::_set_print_ascii_strings(bool print_ascii_strings) {
   m_print_ascii_strings = print_ascii_strings;
   populate_args();
}

void SessionBase::_set_print_leading_zero_hex(bool print_leading_zero_hex) {
   m_print_leading_zero_hex = print_leading_zero_hex;
   populate_args();
}

void SessionBase::_set_print_hex_text(bool print_hex_text) {
   m_print_hex_text = print_hex_text;
   populate_args();
}

void SessionBase::_set_dont_breakdown_oids(bool dont_breakdown_oids) {
   m_dont_breakdown_oids = dont_breakdown_oids;
   populate_args();
}

void SessionBase::_set_escape_quotes_in_indexes(bool escape_quotes_in_indexes) {
   m_escape_quotes_in_indexes = escape_quotes_in_indexes;
   populate_args();
}

void SessionBase::_set_extended_index_format(bool extended_index_format) {
   m_extended_index_format = extended_index_format;
   populate_args();
}

void SessionBase::_set_dont_print_units(bool dont_print_units) {
   m_dont_print_units = dont_print_units;
   populate_args();
}

void SessionBase::_set_output_precision(std::string const& output_precision) {
   m_output_precision = output_precision;
   populate_args();
}

void SessionBase::_set_regex_oid_matching(bool regex_oid_matching) {
   m_regex_oid_matching = regex_oid_matching;
   populate_args();
}

void SessionBase::_set_ignore_display_hints(bool ignore_display_hints) {
   m_ignore_display_hints = ignore_display_hints;
   populate_args();
}

void SessionBase::_set_dont_check_range(bool dont_check_range) {
   m_dont_check_range = dont_check_range;
   populate_args();
}

void SessionBase::_set_random_access_oid(bool random_access_oid) {
   m_random_access_oid = random_access_oid;
   populate_args();
}

void SessionBase::_set_read_ucd_style_oid(bool read_ucd_style_oid) {
   m_read_ucd_style_oid = read_ucd_style_oid;
   populate_args();
}

void SessionBase::_set_oid_suffix(std::string const& oid_suffix) {
   m_oid_suffix = oid_suffix;
   populate_args();
}

void SessionBase::_set_oid_prefix(std::string const& oid_prefix) {
   m_oid_prefix = oid_prefix;
   populate_args();
}

void SessionBase::_set_mib_allow_underline(bool mib_allow_underline) {
   m_mib_allow_underline = mib_allow_underline;
   populate_args();
}

void SessionBase::_set_mib_comment_to_eol(bool mib_comment_to_eol) {
   m_mib_comment_to_eol = mib_comment_to_eol;
   populate_args();
}

void SessionBase::_set_mib_replace_with_latest(bool mib_replace_with_latest) {
   m_mib_replace_with_latest = mib_replace_with_latest;
   populate_args();
}

void SessionBase::_set_non_repeaters(std::string const& non_repeaters) {
   m_non_repeaters = non_repeaters;
   populate_args();
}

void SessionBase::_set_walk_dont_check_lexicographic(bool walk_dont_check_lexicographic) {
   m_walk_dont_check_lexicographic = walk_dont_check_lexicographic;
   populate_args();
}

void SessionBase::_set_walk_include_requested(bool walk_include_requested) {
   m_walk_include_requested = walk_include_requested;
   populate_args();
}

void SessionBase::_set_walk_dont_get_requested(bool walk_dont_get_requested) {
   m_walk_dont_get_requested = walk_dont_get_requested;
   populate_args();
}

void SessionBase::_set_walk_end_oid(std::string const& walk_end_oid) {
   m_walk_end_oid = walk_end_oid;
   populate_args();
}

void SessionBase::_set_dont_fix_pdus(bool dont_fix_pdus) {
   m_dont_fix_pdus = dont_fix_pdus;
   populate_args();
}