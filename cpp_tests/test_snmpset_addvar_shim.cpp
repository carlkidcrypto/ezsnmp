#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "datatypes.h"
#include "exceptionsbase.h"
#include "snmpset.h"

extern "C" int snmp_add_var(netsnmp_pdu *, oid const *, size_t, char, char const *) { return 1; }

class SnmpSetAddVarShimTest : public ::testing::Test {};

TEST_F(SnmpSetAddVarShimTest, TestAddVarFailureThrowsFromSnmpPerror) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysLocation.0", "s", "x"};

   EXPECT_THROW(
       {
          auto results = snmpset(args, "testing_snmpset_addvar_shim");
          (void)results;
       },
       GenericErrorBase);
}
