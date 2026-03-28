#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "snmpgetnext.h"

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;
   *response = NULL;
   return STAT_ERROR;
}

class SnmpGetNextStatErrorShimTest : public ::testing::Test {};

TEST_F(SnmpGetNextStatErrorShimTest, TestStatErrorPathThrows) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "1.3.6.1.2.1.1.1.0"};
   EXPECT_ANY_THROW({ auto results = snmpgetnext(args, "testing_getnext_stat_error_shim"); });
}
