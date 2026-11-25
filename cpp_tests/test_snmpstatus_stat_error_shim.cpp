#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "snmpstatus.h"
#include "test_snmp_response_helpers.h"

static bool g_fail_only_on_getnext = false;

extern "C" int snmp_sess_synch_response(ezsnmp_test::session_handle sessp,
                                        netsnmp_pdu *pdu,
                                        netsnmp_pdu **response) {
   (void)sessp;
   if (g_fail_only_on_getnext && pdu != nullptr && pdu->command == SNMP_MSG_GET) {
      netsnmp_pdu *ok_resp = snmp_pdu_create(SNMP_MSG_RESPONSE);
      ok_resp->errstat = SNMP_ERR_NOERROR;
      ok_resp->errindex = 0;
      *response = ok_resp;
      return STAT_SUCCESS;
   }
   *response = NULL;
   return STAT_ERROR;
}

class SnmpStatusStatErrorShimTest : public ::testing::Test {};

TEST_F(SnmpStatusStatErrorShimTest, TestGetStatErrorPathThrows) {
   g_fail_only_on_getnext = false;
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161"};
   EXPECT_ANY_THROW({ auto results = snmpstatus(args, "testing_status_get_stat_error_shim"); });
}

TEST_F(SnmpStatusStatErrorShimTest, TestGetNextStatErrorPathThrows) {
   g_fail_only_on_getnext = true;
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161"};
   EXPECT_ANY_THROW({ auto results = snmpstatus(args, "testing_status_getnext_stat_error_shim"); });
}
