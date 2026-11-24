#include "thread_safety.h"

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <cstdlib>

// Global mutex definition for Net-SNMP thread safety
std::mutex g_netsnmp_mib_mutex;

// Mutex to serialize per-invocation Net-SNMP global setup (DS flags, snmp_parse_args)
std::mutex g_netsnmp_setup_mutex;

// Mutex to serialize init_snmp / snmp_shutdown lifecycle transitions.
// Threads block on this mutex instead of spin-waiting, eliminating the busy-spin
// race where snmp_shutdown could set g_netsnmp_initialized=false while a new
// thread was already past the spin check but before it called init_snmp.
std::mutex g_netsnmp_lifecycle_mutex;

// Reference counter for init/cleanup
std::atomic<int> g_netsnmp_init_count(0);
std::atomic<bool> g_netsnmp_initialized(false);

namespace {
bool g_netsnmp_library_active = false;
bool g_netsnmp_atexit_registered = false;
std::string g_netsnmp_app_name = "ezsnmp";

void netsnmp_atexit_shutdown() {
   std::lock_guard<std::mutex> lock(g_netsnmp_lifecycle_mutex);
   if (g_netsnmp_library_active) {
      std::lock_guard<std::mutex> mib_lock(g_netsnmp_mib_mutex);
      netsnmp_register_loghandler(NETSNMP_LOGHANDLER_NONE, 0);
      snmp_shutdown(g_netsnmp_app_name.c_str());
      g_netsnmp_library_active = false;
      g_netsnmp_initialized.store(false);
   }
}
} // namespace

void netsnmp_thread_init(std::string const& app_name) {
   std::lock_guard<std::mutex> lock(g_netsnmp_lifecycle_mutex);

   // Increment counter while holding the lifecycle mutex so that the
   // increment, the init_snmp call, and the flag store are all atomic
   // with respect to concurrent cleanup/init calls.
   int count = g_netsnmp_init_count.fetch_add(1);

   // Initialize Net-SNMP once per process on first use rather than re-running
   // init_snmp()/snmp_shutdown() on every single-request Session open/close
   // cycle (fixes GitHub issue #1519).
   if (!g_netsnmp_library_active) {
      std::lock_guard<std::mutex> mib_lock(g_netsnmp_mib_mutex);
      /* completely disable logging otherwise it will default to stderr */
      netsnmp_register_loghandler(NETSNMP_LOGHANDLER_NONE, 0);
      g_netsnmp_app_name = app_name.empty() ? "ezsnmp" : app_name;
      init_snmp(g_netsnmp_app_name.c_str());
      g_netsnmp_library_active = true;
      if (!g_netsnmp_atexit_registered) {
         std::atexit(netsnmp_atexit_shutdown);
         g_netsnmp_atexit_registered = true;
      }
   }
   if (count == 0) {
      g_netsnmp_initialized.store(true);
   }
}

void netsnmp_thread_cleanup(std::string const& app_name) {
   (void)app_name;
   std::lock_guard<std::mutex> lock(g_netsnmp_lifecycle_mutex);

   // Decrement counter while holding the lifecycle mutex so the decrement
   // and flag clear are atomic with respect to any concurrent init call.
   int count = g_netsnmp_init_count.fetch_sub(1);

   // Do not call snmp_shutdown() when count reaches 0 during normal execution:
   // shutting down and re-initializing Net-SNMP on each closed session leaks
   // tclist (4,800 bytes/session) on Net-SNMP 5.9.x and forces repeated MIB
   // re-parsing. NetSnmpProcessShutdownGuard calls snmp_shutdown() once at exit.
   if (count == 1) {
      g_netsnmp_initialized.store(false);
   }
}

namespace {
thread_local SessionFormattingOptions t_session_formatting_options;
} // namespace

void set_thread_formatting_options(SessionFormattingOptions const& opts) {
   t_session_formatting_options = opts;
   t_session_formatting_options.is_set = true;
}

void clear_thread_formatting_options() {
   t_session_formatting_options = SessionFormattingOptions{};
}

SessionFormattingOptions get_thread_formatting_options() { return t_session_formatting_options; }

void apply_current_formatting_options() {
   if (t_session_formatting_options.is_set) {
      netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_PRINT_NUMERIC_ENUM,
                             t_session_formatting_options.print_enums_numerically ? 1 : 0);
      netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_NUMERIC_TIMETICKS,
                             t_session_formatting_options.print_timeticks_numerically ? 1 : 0);

      if (t_session_formatting_options.print_oids_numerically) {
         netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                            NETSNMP_OID_OUTPUT_NUMERIC);
      } else if (t_session_formatting_options.print_full_oids) {
         netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_OID_OUTPUT_FORMAT,
                            NETSNMP_OID_OUTPUT_FULL);
      } else {
         netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_OID_OUTPUT_FORMAT, 0);
      }

      if (t_session_formatting_options.print_hex_strings) {
         netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_STRING_OUTPUT_FORMAT,
                            NETSNMP_STRING_OUTPUT_HEX);
      } else {
         netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_STRING_OUTPUT_FORMAT, 0);
      }
   }
}
