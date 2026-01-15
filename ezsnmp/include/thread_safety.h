#ifndef THREAD_SAFETY_H
#define THREAD_SAFETY_H

#include <mutex>

// Global mutex to protect Net-SNMP MIB parsing operations
// Net-SNMP's MIB tree traversal and shutdown operations are not thread-safe
// This mutex must be used by ALL snmp operations (get, walk, bulkwalk, etc.)
// and by snmp_shutdown to prevent concurrent access to global MIB structures
extern std::mutex g_netsnmp_mib_mutex;

#endif // THREAD_SAFETY_H
