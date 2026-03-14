#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmpget.h"

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;

   netsnmp_pdu *fake_response = snmp_pdu_create(SNMP_MSG_RESPONSE);
   fake_response->errstat = SNMP_ERR_GENERR;
   fake_response->errindex = 1;

   oid name[] = {1, 3, 6, 1, 2, 1, 1, 1, 0};
   long value = 1;
   snmp_varlist_add_variable(&fake_response->variables, name, OID_LENGTH(name), ASN_INTEGER,
                             reinterpret_cast<u_char *>(&value), sizeof(value));

   *response = fake_response;
   return STAT_SUCCESS;
}

extern "C" netsnmp_pdu *snmp_fix_pdu(netsnmp_pdu *pdu, int command) {
   (void)pdu;
   (void)command;
   return NULL;
}

class SnmpGetErrindexShimTest : public ::testing::Test {};

TEST_F(SnmpGetErrindexShimTest, TestErrindexPacketErrorWithoutRetryPdu) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161", "1.3.6.1.2.1.1.6.0"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpget(args, "testing_get_errindex_shim");
          } catch (PacketErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("Error in packet") != std::string::npos);
             EXPECT_TRUE(msg.find("Failed object") != std::string::npos);
             throw;
          }
       },
       PacketErrorBase);
}
