/* Packet-error shim for snmpset - covers the errindex != 0 error message path.
 * snmpset had no packet-error shim before; all other ops did. */
#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "datatypes.h"
#include "exceptionsbase.h"
#include "snmpset.h"

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;

   netsnmp_pdu *fake_response = snmp_pdu_create(SNMP_MSG_RESPONSE);
   fake_response->errstat = SNMP_ERR_GENERR;
   fake_response->errindex = 2;

   oid name1[] = {1, 3, 6, 1, 2, 1, 1, 5, 0};
   long value1 = 1;
   snmp_varlist_add_variable(&fake_response->variables, name1, OID_LENGTH(name1), ASN_INTEGER,
                             reinterpret_cast<u_char *>(&value1), sizeof(value1));

   oid name2[] = {1, 3, 6, 1, 2, 1, 1, 6, 0};
   long value2 = 2;
   snmp_varlist_add_variable(&fake_response->variables, name2, OID_LENGTH(name2), ASN_INTEGER,
                             reinterpret_cast<u_char *>(&value2), sizeof(value2));

   *response = fake_response;
   return STAT_SUCCESS;
}

class SnmpSetShimTest : public ::testing::Test {};

TEST_F(SnmpSetShimTest, TestPacketErrorFromShim) {
   std::vector<std::string> args = {
       "-v", "2c",           "-c", "public", "localhost:11161", "SNMPv2-MIB::sysLocation.0",
       "s",  "test_location"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpset(args, "testing_set_shim");
          } catch (PacketErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("Error in packet") != std::string::npos);
             EXPECT_TRUE(msg.find("Failed object") != std::string::npos);
             throw;
          }
       },
       PacketErrorBase);
}
