#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "datatypes.h"
#include "snmpset.h"

extern "C" int snmp_sess_synch_response(void *sessp, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)sessp;
   (void)pdu;
   *response = NULL;
   return STAT_ERROR;
}

class SnmpSetStatErrorShimTest : public ::testing::Test {};

TEST_F(SnmpSetStatErrorShimTest, TestStatErrorPathThrows) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "1.3.6.1.2.1.1.6.0", "s", "abc"};
   EXPECT_ANY_THROW({ auto results = snmpset(args, "testing_set_stat_error_shim"); });
}
