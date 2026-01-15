#include "thread_safety.h"

// Global mutex definition for Net-SNMP thread safety
std::mutex g_netsnmp_mib_mutex;
