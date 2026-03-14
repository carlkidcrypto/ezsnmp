#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "datatypes.h"
#include "exceptionsbase.h"
#include "snmpbulkwalk.h"

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;
   *response = NULL;
   return STAT_SUCCESS;
}

class SnmpBulkWalkNullShimTest : public ::testing::Test {};

TEST_F(SnmpBulkWalkNullShimTest, TestNullResponseThrowsPacketError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkwalk(args, "testing_bulkwalk_null_shim");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}

TEST_F(SnmpBulkWalkNullShimTest, TestNullResponseWithCiFlagThrowsPacketError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Ci", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkwalk(args, "testing_bulkwalk_null_shim_ci");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}
