#ifndef THREAD_SAFETY_H
#define THREAD_SAFETY_H

#include <atomic>
#include <mutex>

// Global mutex to protect Net-SNMP MIB parsing operations
// Net-SNMP's MIB tree traversal and shutdown operations are not thread-safe
// This mutex must be used by ALL snmp operations (get, walk, bulkwalk, etc.)
// and by snmp_shutdown to prevent concurrent access to global MIB structures
extern std::mutex g_netsnmp_mib_mutex;

// Mutex to serialize Net-SNMP global setup operations per invocation.
// Protects resetting and reading NETSNMP_DS_APPLICATION_ID flags as well as
// calling snmp_parse_args, which modifies global Net-SNMP option state.
extern std::mutex g_netsnmp_setup_mutex;

// Reference counter to track how many sessions are active
// Only the first thread to use snmp will call init_snmp
// Only the last thread to finish will call snmp_shutdown
extern std::atomic<int> g_netsnmp_init_count;

// Flag to track if init_snmp has been called
extern std::atomic<bool> g_netsnmp_initialized;

#include <string>

// Increment reference count and initialize snmp if needed
void netsnmp_thread_init(std::string const& app_name);

// Decrement reference count and cleanup snmp if last thread
void netsnmp_thread_cleanup(std::string const& app_name);

#endif // THREAD_SAFETY_H
