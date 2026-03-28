/* Stateful shim that returns a valid NOERROR response first so the main walk loop body
 * (numprinted++, OID-range check, memmove(name), TIME_RESULTS_SINGLE print) is covered.
 *
 *   Call 1 → NOERROR, var OID {1,3,6,1,2,1} which is inside the walked subtree
 *              {1.3.6.1.2} … {1.3.6.1.3}: numprinted++, name updated, walk continues.
 *   Call 2 → NOSUCHNAME: stops the loop.
 */
#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmpwalk.h"

static int snmpwalk_data_call_count = 0;

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;

   ++snmpwalk_data_call_count;

   netsnmp_pdu *fake_response = snmp_pdu_create(SNMP_MSG_RESPONSE);

   if (snmpwalk_data_call_count == 1) {
      /* NOERROR with a variable whose OID is within the walked subtree.
       * root = {1,3,6,1,2}, end_oid = {1,3,6,1,3}
       * var OID {1,3,6,1,2,1} is in (root, end_oid). */
      fake_response->errstat = SNMP_ERR_NOERROR;
      fake_response->errindex = 0;

      oid var_name[] = {1, 3, 6, 1, 2, 1};
      long var_value = 100;
      snmp_varlist_add_variable(&fake_response->variables, var_name, OID_LENGTH(var_name),
                                ASN_INTEGER, reinterpret_cast<u_char *>(&var_value),
                                sizeof(var_value));
   } else {
      /* Stop the loop: NOSUCHNAME on call 2+. */
      fake_response->errstat = SNMP_ERR_NOSUCHNAME;
      fake_response->errindex = 0;
   }

   *response = fake_response;
   return STAT_SUCCESS;
}

class SnmpWalkWithDataShimTest : public ::testing::Test {
  protected:
   void SetUp() override { snmpwalk_data_call_count = 0; }
};

/* Covers numprinted++, OID-range check (within subtree), memmove(name,vars->name),
 * name_length update, and the non-exception-type branch in the for-loop body. */
TEST_F(SnmpWalkWithDataShimTest, TestNormalWalkLoopBodyWithValidData) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161", "1.3.6.1.2"};

   EXPECT_NO_THROW({
      auto results = snmpwalk(args, "testing_walk_data_shim");
      /* Should have captured at least the one valid variable. */
      EXPECT_GE(results.size(), static_cast<size_t>(1));
   });
}

/* With -CT: covers the TIME_RESULTS_SINGLE per-variable print block
 * (lines ~356-362 inside the NOERROR for-loop). */
TEST_F(SnmpWalkWithDataShimTest, TestTimeResultsSingleCoversPerVariablePrint) {
   std::vector<std::string> args = {"-v",       "2c", "-c", "public", "-CT", "localhost:11161",
                                    "1.3.6.1.2"};

   EXPECT_NO_THROW({
      auto results = snmpwalk(args, "testing_walk_data_shim_ct");
      EXPECT_GE(results.size(), static_cast<size_t>(1));
   });
}

/* With -Ct + -Cp: covers TIME_RESULTS tv1 capture (line ~316 pre-loop) and the
 * post-loop tv2 capture + PRINT_STATISTICS printf (lines ~408, ~417, ~420-421). */
TEST_F(SnmpWalkWithDataShimTest, TestTimeResultsAndStatsCoverPostLoopOutput) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Ct", "-Cp", "localhost:11161", "1.3.6.1.2"};

   EXPECT_NO_THROW({
      auto results = snmpwalk(args, "testing_walk_data_shim_ct_cp");
      EXPECT_GE(results.size(), static_cast<size_t>(1));
   });
}
