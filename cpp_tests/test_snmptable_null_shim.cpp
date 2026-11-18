#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmptable.h"
#include "test_snmp_response_helpers.h"

extern "C" int snmp_sess_synch_response(ezsnmp_test::session_handle sessp,
                                        netsnmp_pdu *pdu,
                                        netsnmp_pdu **response) {
   (void)sessp;
   (void)pdu;
   *response = nullptr;
   return STAT_SUCCESS;
}

class SnmpTableNullShimTest : public ::testing::Test {};

TEST_F(SnmpTableNullShimTest, TestGetBulkNullResponseThrowsPacketError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};

   EXPECT_THROW(
       {
          try {
             auto results = snmptable(args, "testing_table_null_shim");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_sess_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}

TEST_F(SnmpTableNullShimTest, TestGetNextNullResponseThrowsPacketError) {
   std::vector<std::string> args = {
       "-CB", "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};

   EXPECT_THROW(
       {
          try {
             auto results = snmptable(args, "testing_table_null_shim_cb");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_sess_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}
