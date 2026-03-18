#include "thread_safety.h"

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

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

void netsnmp_thread_init(std::string const& app_name) {
   std::lock_guard<std::mutex> lock(g_netsnmp_lifecycle_mutex);

   // Increment counter while holding the lifecycle mutex so that the
   // increment, the init_snmp call, and the flag store are all atomic
   // with respect to concurrent cleanup/init calls.
   int count = g_netsnmp_init_count.fetch_add(1);

   // Only the first thread (count == 0 before increment) calls init_snmp
   if (count == 0) {
      std::lock_guard<std::mutex> mib_lock(g_netsnmp_mib_mutex);
      /* completely disable logging otherwise it will default to stderr */
      netsnmp_register_loghandler(NETSNMP_LOGHANDLER_NONE, 0);
      init_snmp(app_name.c_str());
      g_netsnmp_initialized.store(true, std::memory_order_release);
   }
}

void netsnmp_thread_cleanup(std::string const& app_name) {
   std::lock_guard<std::mutex> lock(g_netsnmp_lifecycle_mutex);

   // Decrement counter while holding the lifecycle mutex so the decrement,
   // the snmp_shutdown call, and the flag clear are all atomic with respect
   // to any concurrent init call.
   int count = g_netsnmp_init_count.fetch_sub(1);

   // Only the last thread (count == 1 before decrement, 0 after) calls snmp_shutdown
   if (count == 1) {
      std::lock_guard<std::mutex> mib_lock(g_netsnmp_mib_mutex);
      /* completely disable logging otherwise it will default to stderr */
      netsnmp_register_loghandler(NETSNMP_LOGHANDLER_NONE, 0);
      snmp_shutdown(app_name.c_str());
      g_netsnmp_initialized.store(false, std::memory_order_release);
   }
}
