#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmpget.h"

static bool g_retry_mode = false;
static int g_call_count = 0;

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;

   ++g_call_count;

   netsnmp_pdu *fake_response = snmp_pdu_create(SNMP_MSG_RESPONSE);

   if (g_retry_mode && g_call_count > 1) {
      fake_response->errstat = SNMP_ERR_NOERROR;
      fake_response->errindex = 0;

      oid ok_name[] = {1, 3, 6, 1, 2, 1, 1, 6, 0};
      long ok_value = 1;
      snmp_varlist_add_variable(&fake_response->variables, ok_name, OID_LENGTH(ok_name),
                                ASN_INTEGER, reinterpret_cast<u_char *>(&ok_value),
                                sizeof(ok_value));
   } else {
      fake_response->errstat = SNMP_ERR_GENERR;
      fake_response->errindex = g_retry_mode ? 2 : 1;

      oid name1[] = {1, 3, 6, 1, 2, 1, 1, 5, 0};
      long value1 = 1;
      snmp_varlist_add_variable(&fake_response->variables, name1, OID_LENGTH(name1), ASN_INTEGER,
                                reinterpret_cast<u_char *>(&value1), sizeof(value1));

      oid name2[] = {1, 3, 6, 1, 2, 1, 1, 6, 0};
      long value2 = 2;
      snmp_varlist_add_variable(&fake_response->variables, name2, OID_LENGTH(name2), ASN_INTEGER,
                                reinterpret_cast<u_char *>(&value2), sizeof(value2));
   }

   *response = fake_response;
   return STAT_SUCCESS;
}

extern "C" netsnmp_pdu *snmp_fix_pdu(netsnmp_pdu *pdu, int command) {
   (void)command;
   if (g_retry_mode) {
      (void)pdu;
      return snmp_pdu_create(SNMP_MSG_GET);
   }
   (void)pdu;
   return NULL;
}

class SnmpGetErrindexShimTest : public ::testing::Test {};

TEST_F(SnmpGetErrindexShimTest, TestErrindexPacketErrorWithoutRetryPdu) {
   g_retry_mode = false;
   g_call_count = 0;

   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "1.3.6.1.2.1.1.6.0"};

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

TEST_F(SnmpGetErrindexShimTest, TestRetryPathSucceedsAfterFixPdu) {
   g_retry_mode = true;
   g_call_count = 0;

   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "1.3.6.1.2.1.1.6.0"};

   EXPECT_NO_THROW({
      auto results = snmpget(args, "testing_get_errindex_retry_shim");
      EXPECT_FALSE(results.empty());
   });
}
