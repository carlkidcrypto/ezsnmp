/* NOSUCHNAME shim for snmpbulkwalk: covers the NOSUCHNAME stop path, the numprinted==0
 * fallback call to snmpbulkwalk_snmp_get_and_print, and flag-gated statistics output.
 */
#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "datatypes.h"
#include "exceptionsbase.h"
#include "snmpbulkwalk.h"

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

class SnmpBulkWalkNoSuchNameShimTest : public ::testing::Test {};

/* Base case: NOSUCHNAME stops the walk loop; numprinted==0 triggers the
 * snmpbulkwalk_snmp_get_and_print fallback path. */
TEST_F(SnmpBulkWalkNoSuchNameShimTest, TestNoSuchNameStopsWalkCleanly) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_NO_THROW({
      auto results = snmpbulkwalk(args, "testing_bulkwalk_nosuchname");
      (void)results;
   });
}

/* -Cp: covers NETSNMP_DS_WALK_PRINT_STATISTICS post-loop printf. */
TEST_F(SnmpBulkWalkNoSuchNameShimTest, TestPrintStatisticsFlagCoversOutput) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cp", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_NO_THROW({
      auto results = snmpbulkwalk(args, "testing_bulkwalk_nosuchname_stats");
      (void)results;
   });
}

/* Default OID (no OID arg): covers the memmove(root, snmpbulkwalk_objid_mib) path. */
TEST_F(SnmpBulkWalkNoSuchNameShimTest, TestDefaultOidPathWhenNoOidGiven) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161"};

   EXPECT_NO_THROW({
      auto results = snmpbulkwalk(args, "testing_bulkwalk_nosuchname_default_oid");
      (void)results;
   });
}

/* -Cc: covers NETSNMP_DS_WALK_DONT_CHECK_LEXICOGRAPHIC toggle in optProc. */
TEST_F(SnmpBulkWalkNoSuchNameShimTest, TestDontCheckLexicographicFlag) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cc", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_NO_THROW({
      auto results = snmpbulkwalk(args, "testing_bulkwalk_nosuchname_cc");
      (void)results;
   });
}

/* -Cn5: covers the non-repeaters numeric parsing branch in optProc. */
TEST_F(SnmpBulkWalkNoSuchNameShimTest, TestNonRepeatersFlagCoversNumericParsing) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cn5", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_NO_THROW({
      auto results = snmpbulkwalk(args, "testing_bulkwalk_nosuchname_cn");
      (void)results;
   });
}

/* -Cr5: covers the max-repeaters numeric parsing branch in optProc. */
TEST_F(SnmpBulkWalkNoSuchNameShimTest, TestMaxRepeatersFlagCoversNumericParsing) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cr5", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_NO_THROW({
      auto results = snmpbulkwalk(args, "testing_bulkwalk_nosuchname_cr");
      (void)results;
   });
}

/* -Ci: covers NETSNMP_DS_WALK_INCLUDE_REQUESTED toggle in optProc. */
TEST_F(SnmpBulkWalkNoSuchNameShimTest, TestIncludeRequestedFlagCoversOptProc) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Ci", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   /* The -Ci flag calls snmpbulkwalk_snmp_get_and_print before the bulk loop.
    * With NOSUCHNAME the nested GET returns cleanly, then the bulk loop also stops. */
   EXPECT_NO_THROW({
      auto results = snmpbulkwalk(args, "testing_bulkwalk_nosuchname_ci");
      (void)results;
   });
}

/* Unknown -C flag: covers the default ParseErrorBase throw in optProc. */
TEST_F(SnmpBulkWalkNoSuchNameShimTest, TestUnknownCFlagThrowsParseError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-CZ", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkwalk(args, "testing_bulkwalk_nosuchname_unknown_flag");
          } catch (ParseErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("Unknown flag") != std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}
