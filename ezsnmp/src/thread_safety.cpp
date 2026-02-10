#include "thread_safety.h"

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

// Global mutex definition for Net-SNMP thread safety
std::mutex g_netsnmp_mib_mutex;

// Reference counter for init/cleanup
std::atomic<int> g_netsnmp_init_count(0);
std::atomic<bool> g_netsnmp_initialized(false);

void netsnmp_thread_init(std::string const& app_name) {
   // Increment counter atomically
   int count = g_netsnmp_init_count.fetch_add(1);

   // Only the first thread (count == 0 before increment) calls init_snmp
   if (count == 0) {
      std::lock_guard<std::mutex> lock(g_netsnmp_mib_mutex);
      /* completely disable logging otherwise it will default to stderr */
      netsnmp_register_loghandler(NETSNMP_LOGHANDLER_NONE, 0);
      /* suppress MIB parse warnings (e.g. "Cannot find module", "Did not find")
         that net-snmp emits when system MIBs reference missing IANA/IEEE modules */
      netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_MIB_WARNINGS, 0);
      init_snmp(app_name.c_str());
      /* Re-apply after init_snmp() in case it re-reads config or resets logging */
      netsnmp_register_loghandler(NETSNMP_LOGHANDLER_NONE, 0);
      netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_MIB_WARNINGS, 0);
      g_netsnmp_initialized.store(true);
   }
}

void netsnmp_thread_cleanup(std::string const& app_name) {
   // Decrement counter atomically
   int count = g_netsnmp_init_count.fetch_sub(1);

   // Only the last thread (count == 1 before decrement, 0 after) calls snmp_shutdown
   if (count == 1) {
      std::lock_guard<std::mutex> lock(g_netsnmp_mib_mutex);
      /* completely disable logging otherwise it will default to stderr */
      netsnmp_register_loghandler(NETSNMP_LOGHANDLER_NONE, 0);
      snmp_shutdown(app_name.c_str());
      g_netsnmp_initialized.store(false);
   }
}
