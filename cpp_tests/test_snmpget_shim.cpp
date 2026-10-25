#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmpget.h"
#include "test_snmp_response_helpers.h"

extern "C" int snmp_sess_synch_response(void *sessp,
                                        netsnmp_pdu *pdu,
                                        netsnmp_pdu **response) {
   (void)sessp;
   (void)pdu;
   *response = make_snmp_generr_response();
   return STAT_SUCCESS;
}

class SnmpGetShimTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SnmpGetShimTest, TestPacketErrorFromShim) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysLocation.0"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpget(args, "testing_get_shim");
          } catch (PacketErrorBase const &e) {
             std::string error_msg(e.what());
             EXPECT_TRUE(error_msg.find("Error in packet") != std::string::npos);
             EXPECT_TRUE(error_msg.find("Failed object") != std::string::npos);
             throw;
          }
       },
       PacketErrorBase);
}
