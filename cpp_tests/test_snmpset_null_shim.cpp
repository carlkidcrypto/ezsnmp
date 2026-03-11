#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmpset.h"

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;
   *response = NULL;
   return STAT_SUCCESS;
}

class SnmpSetNullShimTest : public ::testing::Test {};

TEST_F(SnmpSetNullShimTest, TestNullResponseThrowsPacketError) {
   std::vector<std::string> args = {
       "-v", "2c",           "-c", "public", "localhost:11161", "SNMPv2-MIB::sysLocation.0",
       "s",  "test_location"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpset(args, "testing_set_null_shim");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}
