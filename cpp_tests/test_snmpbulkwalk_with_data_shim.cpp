/* Stateful shim that returns a valid NOERROR response first so the main bulkwalk
 * loop body (numprinted++, OID-range check, memmove(name), name_length update)
 * is covered.
 *
 *   Call 1 → NOERROR with var OID {1,3,6,1,2,1} inside subtree {1.3.6.1.2}
 *   Call 2 → NOSUCHNAME to stop the loop.
 */
#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "datatypes.h"
#include "exceptionsbase.h"
#include "snmpbulkwalk.h"

static int snmpbulkwalk_data_call_count = 0;

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;

   ++snmpbulkwalk_data_call_count;

   netsnmp_pdu *fake_response = snmp_pdu_create(SNMP_MSG_RESPONSE);

   if (snmpbulkwalk_data_call_count == 1) {
      fake_response->errstat = SNMP_ERR_NOERROR;
      fake_response->errindex = 0;

      oid var_name[] = {1, 3, 6, 1, 2, 1};
      long var_value = 100;
      snmp_varlist_add_variable(&fake_response->variables, var_name, OID_LENGTH(var_name),
                                ASN_INTEGER, reinterpret_cast<u_char *>(&var_value),
                                sizeof(var_value));
   } else {
      fake_response->errstat = SNMP_ERR_NOSUCHNAME;
      fake_response->errindex = 0;
   }

   *response = fake_response;
   return STAT_SUCCESS;
}

class SnmpBulkWalkWithDataShimTest : public ::testing::Test {
  protected:
   void SetUp() override { snmpbulkwalk_data_call_count = 0; }
};

TEST_F(SnmpBulkWalkWithDataShimTest, TestNormalBulkWalkLoopBodyWithValidData) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161", "1.3.6.1.2"};

   EXPECT_NO_THROW({
      auto results = snmpbulkwalk(args, "testing_bulkwalk_data_shim");
      EXPECT_GE(results.size(), static_cast<size_t>(1));
   });
}
