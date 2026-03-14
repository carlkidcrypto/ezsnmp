/* NOSUCHNAME shim for snmpwalk: covers the NOSUCHNAME stop path, the numprinted==0
 * fallback call to snmpwalk_snmp_get_and_print, and flag-gated timing/statistics output.
 *
 * The shim always returns SNMP_ERR_NOSUCHNAME which causes the walk loop to stop cleanly
 * (running=0, status=STAT_SUCCESS, numprinted=0).  The function then calls
 * snmpwalk_snmp_get_and_print as a last-resort GET, which also hits the shim.
 * Because errstat != NOERROR the nested GET loop body is not covered here; for that see
 * test_snmpwalk_get_and_print_shim.cpp.
 *
 * Additional test cases pass -C flags so that option-specific code in snmpwalk_optProc
 * and the post-loop statistics/timing sections are covered.
 */
#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmpwalk.h"

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu,
                                   netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;

   netsnmp_pdu *fake_response = snmp_pdu_create(SNMP_MSG_RESPONSE);
   fake_response->errstat  = SNMP_ERR_NOSUCHNAME;
   fake_response->errindex = 0;

   *response = fake_response;
   return STAT_SUCCESS;
}

class SnmpWalkNoSuchNameShimTest : public ::testing::Test {};

/* Base case: NOSUCHNAME stops the walk loop cleanly; numprinted==0 triggers the
 * snmpwalk_snmp_get_and_print fallback path (lines ~395-401 in snmpwalk.cpp). */
TEST_F(SnmpWalkNoSuchNameShimTest, TestNoSuchNameStopsWalkCleanly) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   /* Should NOT throw - NOSUCHNAME ends the walk silently. */
   EXPECT_NO_THROW({
      auto results = snmpwalk(args, "testing_walk_nosuchname");
      (void)results;
   });
}

/* -Cp: exercises NETSNMP_DS_WALK_PRINT_STATISTICS post-loop output (line ~417). */
TEST_F(SnmpWalkNoSuchNameShimTest, TestPrintStatisticsFlagCoversStatisticsOutput) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cp", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_NO_THROW({
      auto results = snmpwalk(args, "testing_walk_nosuchname_stats");
      (void)results;
   });
}

/* -Ct: exercises NETSNMP_DS_WALK_TIME_RESULTS clock calls (lines ~408, ~420-421). */
TEST_F(SnmpWalkNoSuchNameShimTest, TestTimeResultsFlagCoversTimingOutput) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Ct", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_NO_THROW({
      auto results = snmpwalk(args, "testing_walk_nosuchname_time");
      (void)results;
   });
}

/* -CT: exercises NETSNMP_DS_WALK_TIME_RESULTS_SINGLE inside the walk loop (lines ~316, ~322). */
TEST_F(SnmpWalkNoSuchNameShimTest, TestTimeResultsSingleFlagCoversPerRequestTiming) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-CT", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_NO_THROW({
      auto results = snmpwalk(args, "testing_walk_nosuchname_time_single");
      (void)results;
   });
}

/* Default OID (no OID arg): covers the memmove(root, objid_mib) fallback (line ~242). */
TEST_F(SnmpWalkNoSuchNameShimTest, TestDefaultOidPathWhenNoOidGiven) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161"};

   EXPECT_NO_THROW({
      auto results = snmpwalk(args, "testing_walk_nosuchname_default_oid");
      (void)results;
   });
}

/* -CE end_name: covers the snmp_parse_oid(end_name) block (lines ~259-265). */
TEST_F(SnmpWalkNoSuchNameShimTest, TestEndNameFlagCoversEndOidParsing) {
   std::vector<std::string> args = {"-v",           "2c",      "-c",       "public",
                                    "-CE",           "1.3.6.1.2.1.10",
                                    "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_NO_THROW({
      auto results = snmpwalk(args, "testing_walk_nosuchname_end_name");
      (void)results;
   });
}
