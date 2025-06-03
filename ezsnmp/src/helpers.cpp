
#include "helpers.h"

#include <cstring>
#include <iostream>
#include <regex>
#include <sstream>

#include "exceptionsbase.h"

/* straight copy from
 * https://github.com/net-snmp/net-snmp/blob/d5afe2e9e02def1c2d663828cd1e18108183d95e/snmplib/mib.c#L3456
 */
/* Slight modifications to return std::string instead of print to stdout */
std::string print_variable_to_string(oid const *objid,
                                     size_t objidlen,
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

   if (message.find("Unknown host") != std::string::npos) {
      message = message.substr(0, message.find_last_not_of(' ') + 1);

      throw ConnectionErrorBase(message);
   }

   if (message.find("Timeout") != std::string::npos) {
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
   int xerr = snmp_errno; // MTCRITICAL_RESOURCE
   char const *str = snmp_api_errstring(xerr);

   // Construct the error message
   std::string message = std::string(prog_string) + ": " + str;

   // Throw a runtime_error with the message
   throw GenericErrorBase(message);
}

// This is a helper to create the argv that the netsnmp functions like snmpwalk(), snmpget(), etc
// expect
std::unique_ptr<char *[], Deleter> create_argv(std::vector<std::string> const &args, int &argc) {
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
        \.?\d+(?:\.\d+)*               # numeric OID
        |                              # or
        (?:\w+(?:[-:]*\w+)+)          # regular OID
        |                              # or
        (?:\.?iso(?:\.\w+[-:]*\w+)+)  # fully qualified OID
    )
    \.?(.*)                            # OID index
)");

// This regular expression takes an OID string and splits it into
// the base OID and the index. It works for OIDs with formats like:
//  - 'SNMPv2::mib-2.17.7.1.4.3.1.2.300'
//  - 'NET-SNMP-AGENT-MIB::nsCacheStatus.1.3.6.1.2.1.4.24.4'
std::regex const OID_INDEX_RE2(R"(^(.+)\.([^.]+)$)");

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

   // Extract value and trim leading/trailing whitespace
   std::getline(ss, temp);
   result.value = temp.substr(1);
   result.value = result.value.substr(0, result.value.find_last_not_of(" \t\n\r") + 1);

   // Check for "No Such Object" in the value
   if (result.value.find("No Such Object") != std::string::npos) {
      result.type = "NOSUCHOBJECT";
   }
   // Check for "No Such Instance" in the value
   else if (result.value.find("No Such Instance") != std::string::npos) {
      result.type = "NOSUCHINSTANCE";
   }

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

// This is a helper to remove V3 users from the cache when V3 information changes
void remove_v3_user_from_cache(std::string const &security_name_str,
                               std::string const &context_engine_id_str) {
   // std::cout << "security_name_str: " << security_name_str.c_str() << std::endl;
   // std::cout << "context_engine_id_str:" << context_engine_id_str.c_str() << std::endl;
   struct usmUser *actUser = usm_get_userList();

   while (actUser != NULL) {
      struct usmUser *dummy = actUser;
      auto act_user_sec_name_str = std::string("");
      auto act_user_engine_id_str = std::string("");

      if (actUser->secName != NULL) {
         act_user_sec_name_str = std::string(actUser->secName);
      }
      if (actUser->engineID != NULL) {
         act_user_engine_id_str = std::string(reinterpret_cast<char *>(actUser->engineID));
      }

      // if (!act_user_sec_name_str.empty() && !act_user_engine_id_str.empty() &&
      //     security_name_str == act_user_sec_name_str &&
      //     context_engine_id_str == act_user_engine_id_str) {
      //    std::cout << "Removing user: " << security_name_str.c_str() << std::endl;
      //    usm_remove_user(actUser);
      //    actUser->next = NULL;
      //    actUser->prev = NULL;
      //    usm_free_user(actUser);
      //    break;
      // }

      // This works for now, but it may change when threads/muli-procs are involved.
      if (!act_user_sec_name_str.empty() && !act_user_engine_id_str.empty() &&
          security_name_str == act_user_sec_name_str &&
          context_engine_id_str == act_user_engine_id_str) {
         // std::cout << "Removing user: " << security_name_str.c_str() << std::endl;
         usm_remove_user(actUser);
         actUser->next = NULL;
         actUser->prev = NULL;
         usm_free_user(actUser);
         break;
      } else if (!act_user_sec_name_str.empty() && security_name_str == act_user_sec_name_str) {
         // std::cout << "Removing user: " << security_name_str.c_str() << std::endl;
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
      netsnmp_sprint_realloc_objid_tree(&buf, &buf_len, &out_len, 1, &buf_overflow, objid,
                                        objidlen);
      if (buf_overflow) {
         ss << buf << " [TRUNCATED]\n";
      } else {
         ss << buf << "\n";
      }
   }

   SNMP_FREE(buf);
   return ss.str();
}

#if IS_SUPPORTED_PACKAGE_VERSION

/* Free the memory owned by a session but not the session object itself. */
void netsnmp_cleanup_session(netsnmp_session *s) {
   free(s->localname);
   free(s->peername);
   free(s->community);
   free(s->contextEngineID);
   free(s->contextName);
   free(s->securityEngineID);
   free(s->securityName);
   free(s->securityAuthProto);
   free(s->securityAuthLocalKey);
   free(s->securityPrivProto);
   free(s->securityPrivLocalKey);
   free(s->paramName);
   // #ifndef NETSNMP_NO_TRAP_STATS
   // free(s->trap_stats);
   // #endif /* NETSNMP_NO_TRAP_STATS */
   // usm_free_user(s->sessUser);
   memset(s, 0, sizeof(*s));
}

/**
 * Query the current value of the monotonic clock.
 *
 * Returns the current value of a monotonic clock if such a clock is provided by
 * the operating system or the wall clock time if no such clock is provided by
 * the operating system. A monotonic clock is a clock that is never adjusted
 * backwards and that proceeds at the same rate as wall clock time.
 *
 * @param[out] tv Pointer to monotonic clock time.
 */
void netsnmp_get_monotonic_clock(struct timeval *tv) {
#if defined(HAVE_CLOCK_GETTIME) && defined(CLOCK_MONOTONIC)
   struct timespec ts;
   int res;

   res = clock_gettime(CLOCK_MONOTONIC, &ts);
   if (res >= 0) {
      tv->tv_sec = ts.tv_sec;
      tv->tv_usec = ts.tv_nsec / 1000;
   } else {
      gettimeofday(tv, NULL);
   }
#elif defined(WIN32)
   /*
    * Windows: return tick count. Note: the rate at which the tick count
    * increases is not adjusted by the time synchronization algorithm, so
    * expect an error of <= 100 ppm for the rate at which this clock
    * increases.
    */
   typedef ULONGLONG(WINAPI * pfGetTickCount64)(void);
   static int s_initialized;
   static pfGetTickCount64 s_pfGetTickCount64;
   uint64_t now64;

   if (!s_initialized) {
      HMODULE hKernel32 = GetModuleHandle("kernel32");
      s_pfGetTickCount64 = (pfGetTickCount64)GetProcAddress(hKernel32, "GetTickCount64");
      s_initialized = TRUE;
   }

   if (s_pfGetTickCount64) {
      /* Windows Vista, Windows 2008 or any later Windows version */
      now64 = (*s_pfGetTickCount64)();
   } else {
      /* Windows XP, Windows 2003 or any earlier Windows version */
      static uint32_t s_wraps, s_last;
      uint32_t now;

      now = GetTickCount();
      if (now < s_last) {
         s_wraps++;
      }
      s_last = now;
      now64 = ((uint64_t)s_wraps << 32) | now;
   }
   tv->tv_sec = now64 / 1000;
   tv->tv_usec = (now64 % 1000) * 1000;
#else
   /* At least FreeBSD 4 doesn't provide monotonic clock support. */
#warning Not sure how to query a monotonically increasing clock on your system. \
Timers will not work correctly if the system clock is adjusted by e.g. ntpd.
   gettimeofday(tv, NULL);
#endif
}

#endif

void clear_net_snmp_library_data() {
   netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                      0); // Clear -On && Clear -Of
   netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_PRINT_NUMERIC_ENUM, 0); // Clear -Oe
}
