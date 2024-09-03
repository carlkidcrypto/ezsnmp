#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

void
snmpwalk_usage(void);
void
snmpwalk_snmp_get_and_print(netsnmp_session * ss, oid * theoid, size_t theoid_len);
void
snmpwalk_optProc(int argc, char *const *argv, int opt);
int snmpwalk_main(int argc, char *argv[]);