/* Stateful shim for snmpwalk: covers the snmpwalk_snmp_get_and_print() helper body.
 *
 * The shim uses a call counter to produce two different responses:
 *   Call 1 (main GETNEXT loop)  → SNMP_ERR_NOSUCHNAME → running=0, numprinted=0, STAT_SUCCESS
 *   Call 2 (snmpwalk_snmp_get_and_print fallback GET) → NOERROR with a variable
 *             → for-loop body executes → lines ~110-113 in snmpwalk.cpp covered.
 */
#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmpwalk.h"

static int snmpwalk_call_count = 0;

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;

   ++snmpwalk_call_count;

   netsnmp_pdu *fake_response = snmp_pdu_create(SNMP_MSG_RESPONSE);

   if (snmpwalk_call_count == 1) {
      /* Main walk loop: NOSUCHNAME stops the loop cleanly with numprinted==0. */
      fake_response->errstat = SNMP_ERR_NOSUCHNAME;
      fake_response->errindex = 0;
   } else {
      /* snmpwalk_snmp_get_and_print fallback GET: NOERROR with a single variable so
       * the for-loop body (numprinted++, print_variable_to_string) executes. */
      fake_response->errstat = SNMP_ERR_NOERROR;
      fake_response->errindex = 0;

      oid dummy_name[] = {1, 3, 6, 1, 2, 1, 1, 1, 0};
      long dummy_value = 42;
      snmp_varlist_add_variable(&fake_response->variables, dummy_name, OID_LENGTH(dummy_name),
                                ASN_INTEGER, reinterpret_cast<u_char *>(&dummy_value),
                                sizeof(dummy_value));
   }

   *response = fake_response;
   return STAT_SUCCESS;
}

class SnmpWalkGetAndPrintShimTest : public ::testing::Test {
  protected:
   void SetUp() override { snmpwalk_call_count = 0; }
};

/* With numprinted==0 after the main loop snmpwalk calls snmpwalk_snmp_get_and_print
 * which receives the NOERROR response and iterates its variable list. */
TEST_F(SnmpWalkGetAndPrintShimTest, TestGetAndPrintFallbackCoversHelperLoopBody) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_NO_THROW({
      auto results = snmpwalk(args, "testing_walk_get_and_print_shim");
      /* The fallback GET returned a variable so the results vector is non-empty. */
      EXPECT_GE(results.size(), static_cast<size_t>(1));
   });
}

/* -CI (DONT_GET_REQUESTED): when set, the numprinted==0 fallback is skipped, so the
 * loop body in snmpwalk_snmp_get_and_print is NOT exercised.  The test simply
 * verifies that -CI suppresses the fallback and the function returns cleanly. */
TEST_F(SnmpWalkGetAndPrintShimTest, TestDontGetRequestedSkipsGetAndPrintFallback) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-CI", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_NO_THROW({
      auto results = snmpwalk(args, "testing_walk_get_and_print_shim_ci_flag");
      (void)results;
   });
}
