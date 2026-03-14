/* Stateful shim for snmpbulkwalk: covers the snmpbulkwalk_snmp_get_and_print() body.
 *
 *   Call 1 (main GETBULK loop)  → SNMP_ERR_NOSUCHNAME → running=0, numprinted=0
 *   Call 2 (fallback GET)       → NOERROR + variable  → loop body executed
 */
#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "datatypes.h"
#include "exceptionsbase.h"
#include "snmpbulkwalk.h"

static int snmpbulkwalk_call_count = 0;

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu,
                                   netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;

   ++snmpbulkwalk_call_count;

   netsnmp_pdu *fake_response = snmp_pdu_create(SNMP_MSG_RESPONSE);

   if (snmpbulkwalk_call_count == 1) {
      /* Main bulk loop: NOSUCHNAME stops cleanly, numprinted==0. */
      fake_response->errstat  = SNMP_ERR_NOSUCHNAME;
      fake_response->errindex = 0;
   } else {
      /* Fallback GET: NOERROR + variable so the for-loop body executes. */
      fake_response->errstat  = SNMP_ERR_NOERROR;
      fake_response->errindex = 0;

      oid  dummy_name[] = {1, 3, 6, 1, 2, 1, 1, 1, 0};
      long dummy_value  = 42;
      snmp_varlist_add_variable(&fake_response->variables, dummy_name,
                                OID_LENGTH(dummy_name), ASN_INTEGER,
                                reinterpret_cast<u_char *>(&dummy_value),
                                sizeof(dummy_value));
   }

   *response = fake_response;
   return STAT_SUCCESS;
}

class SnmpBulkWalkGetAndPrintShimTest : public ::testing::Test {
  protected:
   void SetUp() override { snmpbulkwalk_call_count = 0; }
};

TEST_F(SnmpBulkWalkGetAndPrintShimTest, TestGetAndPrintFallbackCoversHelperLoopBody) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_NO_THROW({
      auto results = snmpbulkwalk(args, "testing_bulkwalk_get_and_print_shim");
      EXPECT_GE(results.size(), static_cast<size_t>(1));
   });
}
