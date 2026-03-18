#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "datatypes.h"
#include "exceptionsbase.h"
#include "snmpbulkwalk.h"

static bool g_lexicographic_error_mode = false;
static bool g_exception_value_mode = false;

extern "C" int snmp_synch_response(netsnmp_session *, netsnmp_pdu *, netsnmp_pdu **response) {
   netsnmp_pdu *fake_response = snmp_pdu_create(SNMP_MSG_RESPONSE);
   fake_response->errstat = SNMP_ERR_NOERROR;
   fake_response->errindex = 0;

   if (g_lexicographic_error_mode) {
      oid same_name[] = {1, 3, 6, 1, 2};
      long same_value = 1;
      snmp_varlist_add_variable(&fake_response->variables, same_name, OID_LENGTH(same_name),
                                ASN_INTEGER, reinterpret_cast<u_char *>(&same_value),
                                sizeof(same_value));
   } else if (g_exception_value_mode) {
      oid inside_name[] = {1, 3, 6, 1, 2, 1};
      snmp_varlist_add_variable(&fake_response->variables, inside_name, OID_LENGTH(inside_name),
                                SNMP_ENDOFMIBVIEW, nullptr, 0);
   }

   *response = fake_response;
   return STAT_SUCCESS;
}

class SnmpBulkWalkOrderShimTest : public ::testing::Test {
  protected:
   void SetUp() override {
      g_lexicographic_error_mode = false;
      g_exception_value_mode = false;
   }
};

TEST_F(SnmpBulkWalkOrderShimTest, TestLexicographicErrorBranchThrows) {
   g_lexicographic_error_mode = true;
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161", "1.3.6.1.2"};

   EXPECT_THROW(
       {
          auto results = snmpbulkwalk(args, "testing_snmpbulkwalk_order_lexic");
          (void)results;
       },
       GenericErrorBase);
}

TEST_F(SnmpBulkWalkOrderShimTest, TestExceptionValueStopsRunningWithoutThrow) {
   g_exception_value_mode = true;
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161", "1.3.6.1.2"};

   EXPECT_NO_THROW({
      auto results = snmpbulkwalk(args, "testing_snmpbulkwalk_order_exception_type");
      EXPECT_FALSE(results.empty());
   });
}
