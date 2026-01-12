
#include "helpers.h"

#include <algorithm>
#include <cstring>
#include <iostream>
#include <mutex>
#include <regex>
#include <sstream>
#include <string>
#include <utility>

#include "exceptionsbase.h"

/**
 * @brief Returns the global mutex for Net-SNMP library operations.
 *
 * This function returns a reference to a static mutex that protects
 * Net-SNMP global state from concurrent access across threads.
 *
 * Thread-safe operations protected by this mutex:
 * - Library initialization (init_snmp)
 * - MIB parsing operations
 * - SNMPv3 user cache access
 * - Global error code access (snmp_errno)
 */
std::mutex &get_netsnmp_mutex() {
  static std::mutex netsnmp_global_mutex;
  return netsnmp_global_mutex;
}

/* straight copy from
 * https://github.com/net-snmp/net-snmp/blob/d5afe2e9e02def1c2d663828cd1e18108183d95e/snmplib/mib.c#L3456
 */
/* Slight modifications to return std::string instead of print to stdout */
std::string print_variable_to_string(oid const *objid, size_t objidlen,
                                     netsnmp_variable_list const *variable) {
  u_char *buf = nullptr;
  size_t buf_len = 256, out_len = 0;

  if ((buf = static_cast<u_char *>(calloc(buf_len, 1))) == nullptr) {
    return "[TRUNCATED]";
  } else {
    if (sprint_realloc_variable(&buf, &buf_len, &out_len, 1, objid, objidlen,
                                variable)) {
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

/* straight copy from
 * https://github.com/net-snmp/net-snmp/blob/b3163b31ee86930111cf097395cdb33074619cab/snmplib/snmp_api.c#L620-L636
 */
/* Slight modifications to raise GenericError instead of print to stderr */
void snmp_sess_perror_exception(char const *prog_string, netsnmp_session *ss) {
  std::string err;
  char *err_cstr = nullptr;

  snmp_error(ss, NULL, NULL, &err_cstr);
  err = err_cstr;
  SNMP_FREE(err_cstr);
  snmp_close(ss);

  // Construct the error message
  std::string message = std::string(prog_string) + ": " + err;

  // Perform case-insensitive matching for common connection failures across
  // platforms
  std::string message_lower = message;
  std::transform(message_lower.begin(), message_lower.end(),
                 message_lower.begin(), ::tolower);

  auto const is_connection_error = [](std::string const &haystack) {
    return haystack.find("unknown host") != std::string::npos ||
           haystack.find("name or service not known") != std::string::npos ||
           haystack.find("temporary failure in name resolution") !=
               std::string::npos ||
           haystack.find("could not translate host name") !=
               std::string::npos ||
           haystack.find("no address associated with hostname") !=
               std::string::npos;
  };

  auto const is_timeout_error = [](std::string const &haystack) {
    return haystack.find("timeout") != std::string::npos ||
           haystack.find("timed out") != std::string::npos;
  };

  if (is_connection_error(message_lower)) {
    message = message.substr(0, message.find_last_not_of(' ') + 1);
    throw ConnectionErrorBase(message);
  }

  if (is_timeout_error(message_lower)) {
    message = message.substr(0, message.find_last_not_of(' ') + 1);
    throw TimeoutErrorBase(message);
  }

  if (message.find("Cannot send V2 PDU on V1 session") != std::string::npos) {
    message = message.substr(0, message.find_last_not_of(' ') + 1);

    throw PacketErrorBase(message);
  }

  // Throw a runtime_error with the message
  throw GenericErrorBase(message);
}

/* straight copy from
 * https://github.com/net-snmp/net-snmp/blob/b3163b31ee86930111cf097395cdb33074619cab/snmplib/snmp_api.c#L505-L511
 */
/* Slight modifications to raise GenericError instead of print to stderr */
void snmp_perror_exception(char const *prog_string) {
  // Protect access to the global snmp_errno variable with a mutex
  // This is a thread-critical resource marked as MTCRITICAL_RESOURCE
  std::lock_guard<std::mutex> lock(get_netsnmp_mutex());
  int xerr = snmp_errno;
  char const *str = snmp_api_errstring(xerr);

  // Construct the error message
  std::string message = std::string(prog_string) + ": " + str;

  // Throw a runtime_error with the message
  throw GenericErrorBase(message);
}

// This is a helper to create the argv that the netsnmp functions like
// snmpwalk(), snmpget(), etc expect
std::unique_ptr<char *[], Deleter>
create_argv(std::vector<std::string> const &args, int &argc) {
  argc = args.size() + 1;
  std::unique_ptr<char *[], Deleter> argv(new char *[argc + 1]);

  argv[0] = const_cast<char *>("netsnmp");

  for (int i = 0; i < static_cast<int>(args.size()); ++i) {
    argv[i + 1] = strdup(args[i].c_str());

    if (argv[i + 1] == nullptr) {
      throw std::runtime_error("Memory allocation failed for argv element");
    }
  }
  argv[argc] = nullptr;

  return argv;
}

// This regular expression is used to extract the index from an OID
// We attempt to extract the index from an OID (e.g. sysDescr.0
// or .iso.org.dod.internet.mgmt.mib-2.system.sysContact.0)
std::regex const OID_INDEX_RE(R"((
        \.?\d+(?:\.\d+)* # numeric OID
        |                        # or
        (?:\w+(?:[-:]*\w+)+)     # regular OID
        |                        # or
        \.?iso(?:\.\w+[-:]*\w+)+ # fully qualified OID
    )
    \.?(.*)                      # OID index
)");

// This regular expression takes an OID string and splits it into
// the base OID and the index. It works for OIDs with formats like:
//  - 'SNMPv2::mib-2.17.7.1.4.3.1.2.300'
//  - 'NET-SNMP-AGENT-MIB::nsCacheStatus.1.3.6.1.2.1.4.24.4'
std::regex const OID_INDEX_RE2(R"(^(.+)\.([^.]+)$)");

// Matches OIDs that are known to have a multi-component numeric index (e.g.,
// those from the RFC1213-MIB), preventing it from incorrectly matching the
// complex OID.
std::regex const OID_INDEX_RE3(R"(^(RFC1213-MIB::[\w-]+)\.([\d\.]+)$)");

// This is a helper to turn OID results into a Result type
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
  std::smatch third_match;

  if (std::regex_match(result.oid, third_match, OID_INDEX_RE3)) {
    std::string temp_oid = third_match[1].str();
    std::string temp_index = third_match[2].str();
    result.oid = std::move(temp_oid);
    result.index = std::move(temp_index);
  } else if (std::regex_match(result.oid, second_match, OID_INDEX_RE2)) {
    std::string temp_oid = second_match[1].str();
    std::string temp_index = second_match[2].str();
    result.oid = std::move(temp_oid);
    result.index = std::move(temp_index);
  } else if (std::regex_match(result.oid, first_match, OID_INDEX_RE)) {
    std::string temp_oid = first_match[1].str();
    std::string temp_index = first_match[2].str();
    result.oid = std::move(temp_oid);
    result.index = std::move(temp_index);
  } else if (result.oid == ".") {
    result.index = "";
  } else {
    // Default case if no matches are found
    result.index = "";
  }

  // Extract type
  std::getline(ss, temp, ':');
  size_t first_char_pos = temp.find_first_not_of(" \t");
  if (first_char_pos != std::string::npos) {
    result.type = temp.substr(first_char_pos);
  } else {
    result.type = "";
  }

  // Extract value and trim leading/trailing whitespace
  std::getline(ss, temp);
  if (!temp.empty() && temp[0] == ' ') {
    temp.erase(0, 1);
  }
  result.value = temp.substr(0, temp.find_last_not_of(" \t\n\r") + 1);

  // Strip surrounding quotes from values (fix for issue #355)
  // Some net-snmp versions/configurations return string values enclosed in
  // quotes
  if (result.value.length() >= 2 && result.value.front() == '"' &&
      result.value.back() == '"') {
    result.value = result.value.substr(1, result.value.length() - 2);
  }

  // Check for "No Such Object" in the value
  if (result.value.find("No Such Object") != std::string::npos) {
    result.type = "NOSUCHOBJECT";
  }
  // Check for "No Such Instance" in the value
  else if (result.value.find("No Such Instance") != std::string::npos) {
    result.type = "NOSUCHINSTANCE";
  }
  // This might get messy, but we will try to handle it on a case by base basis
  // When -O t is using for print timeticks unparsed as numeric integers let's
  // force the type to INTEGER
  else if (result.oid.find("sysUpTime") != std::string::npos &&
           result.type != "Timeticks") {
    result.type = "Timeticks";
  }

  result.update_converted_value();

  return result;
}

// This is a helper to create a vector of Result types
std::vector<Result> parse_results(std::vector<std::string> const &inputs) {
  std::vector<Result> results;
  for (auto const &input : inputs) {
    results.push_back(parse_result(input));
  }
  return results;
}

// This is a helper to remove V3 users from the cache when V3 information
// changes
void remove_v3_user_from_cache(std::string const &security_name_str,
                               std::string const &context_engine_id_str) {
  // Protect USM user list access with mutex for thread-safety
  // The USM (User-based Security Model) user cache is a global shared resource
  // This fixes the v3 multi-threading issue (#45)
  std::lock_guard<std::mutex> lock(get_netsnmp_mutex());

  // std::cout << "security_name_str: " << security_name_str.c_str() <<
  // std::endl; std::cout << "context_engine_id_str:" <<
  // context_engine_id_str.c_str() << std::endl;
  struct usmUser *actUser = usm_get_userList();

  while (actUser != NULL) {
    struct usmUser *dummy = actUser;
    auto act_user_sec_name_str = std::string("");
    auto act_user_engine_id_str = std::string("");

    if (actUser->secName != NULL) {
      act_user_sec_name_str = std::string(actUser->secName);
    }
    if (actUser->engineID != NULL) {
      act_user_engine_id_str =
          std::string(reinterpret_cast<char *>(actUser->engineID));
    }

    // if (!act_user_sec_name_str.empty() && !act_user_engine_id_str.empty() &&
    //     security_name_str == act_user_sec_name_str &&
    //     context_engine_id_str == act_user_engine_id_str) {
    //    std::cout << "Removing user: " << security_name_str.c_str() <<
    //    std::endl; usm_remove_user(actUser); actUser->next = NULL;
    //    actUser->prev = NULL;
    //    usm_free_user(actUser);
    //    break;
    // }

    // Thread-safe implementation with mutex protection
    if (!act_user_sec_name_str.empty() && !act_user_engine_id_str.empty() &&
        security_name_str == act_user_sec_name_str &&
        context_engine_id_str == act_user_engine_id_str) {
      // std::cout << "Removing user: " << security_name_str.c_str() <<
      // std::endl;
      usm_remove_user(actUser);
      actUser->next = NULL;
      actUser->prev = NULL;
      usm_free_user(actUser);
      break;
    } else if (!act_user_sec_name_str.empty() &&
               security_name_str == act_user_sec_name_str) {
      // std::cout << "Removing user: " << security_name_str.c_str() <<
      // std::endl;
      usm_remove_user(actUser);
      actUser->next = NULL;
      actUser->prev = NULL;
      usm_free_user(actUser);
      break;
    }
    actUser = dummy->next;
  }
}

std::string print_objid_to_string(oid const *objid, size_t objidlen) {
  /* number of subidentifiers */
  u_char *buf = NULL;
  size_t buf_len = 256, out_len = 0;
  int buf_overflow = 0;
  std::stringstream ss;

  if ((buf = static_cast<u_char *>(calloc(buf_len, 1))) == nullptr) {
    ss << "[TRUNCATED]\n";
    return ss.str();
  } else {
    netsnmp_sprint_realloc_objid_tree(&buf, &buf_len, &out_len, 1,
                                      &buf_overflow, objid, objidlen);
    if (buf_overflow) {
      ss << buf << " [TRUNCATED]\n";
    } else {
      ss << buf << "\n";
    }
  }

  SNMP_FREE(buf);
  return ss.str();
}

void clear_net_snmp_library_data() {
  // From:
  // https://github.com/net-snmp/net-snmp/blob/be3f27119346acbcc2e200bb6e33e98677a47b2d/include/net-snmp/library/default_store.h#
  netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                     0); // Clear -O n && Clear -O f
  netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID,
                         NETSNMP_DS_LIB_PRINT_NUMERIC_ENUM,
                         0); // Clear -O e
  netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID,
                         NETSNMP_DS_LIB_NUMERIC_TIMETICKS, 0); // Clear -O t
}

// Thread-safe wrapper for init_snmp()
// Protects library initialization which modifies global state
void thread_safe_init_snmp(const char *app_name) {
  std::lock_guard<std::mutex> lock(get_netsnmp_mutex());
  init_snmp(app_name);
}

// Thread-safe wrapper for snmp_parse_oid()
// Protects OID parsing which accesses global MIB data structures
oid *thread_safe_snmp_parse_oid(const char *argv, oid *name,
                                size_t *name_length) {
  std::lock_guard<std::mutex> lock(get_netsnmp_mutex());
  return snmp_parse_oid(argv, name, name_length);
}

// Thread-safe wrapper for snmp_parse_args()
// Protects argument parsing which may load and parse MIBs
int thread_safe_snmp_parse_args(int argc, char **argv, netsnmp_session *session,
                                const char *localOpts,
                                void (*proc)(int, char *const *, int)) {
  std::lock_guard<std::mutex> lock(get_netsnmp_mutex());
  return snmp_parse_args(argc, argv, session, localOpts, proc);
}