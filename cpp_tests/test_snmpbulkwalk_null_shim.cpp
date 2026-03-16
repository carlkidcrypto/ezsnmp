#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "datatypes.h"
#include "exceptionsbase.h"
#include "snmpbulkwalk.h"

void snmpbulkwalk_usage(void);

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;
   *response = NULL;
   return STAT_SUCCESS;
}

class SnmpBulkWalkNullShimTest : public ::testing::Test {};

TEST_F(SnmpBulkWalkNullShimTest, TestNullResponseThrowsPacketError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkwalk(args, "testing_bulkwalk_null_shim");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}

TEST_F(SnmpBulkWalkNullShimTest, TestNullResponseWithCiFlagThrowsPacketError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Ci", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkwalk(args, "testing_bulkwalk_null_shim_ci");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}

/* Unknown -C sub-flag: snmpbulkwalk_optProc default case throws ParseErrorBase. */
TEST_F(SnmpBulkWalkNullShimTest, TestUnknownCFlagThrowsParseError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-C", "Z", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkwalk(args, "testing_bulkwalk_null_shim_unknown_cflag");
          } catch (ParseErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("Unknown flag") != std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}

/* -Cn with no number: covers the endptr==optarg ParseError branch. */
TEST_F(SnmpBulkWalkNullShimTest, TestNonRepeatersWithoutNumberThrowsParseError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-C", "n", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkwalk(args, "testing_bulkwalk_null_shim_cn_nonumber");
          } catch (ParseErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("No number given for -Cn") != std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}

/* -h triggers NETSNMP_PARSE_ARGS_SUCCESS_EXIT and executes snmpbulkwalk_usage(). */
TEST_F(SnmpBulkWalkNullShimTest, TestHelpFlagThrowsParseErrorForSuccessExit) {
   std::vector<std::string> args = {"-h"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkwalk(args, "testing_bulkwalk_null_shim_help");
          } catch (ParseErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("NETSNMP_PARSE_ARGS_SUCCESS_EXIT") != std::string::npos ||
                         msg.find("PARSE_ARGS") != std::string::npos ||
                         msg.find("USAGE") != std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}

/* Direct usage call covers snmpbulkwalk_usage() function body lines. */
TEST_F(SnmpBulkWalkNullShimTest, TestUsageFunctionDirectCallNoThrow) {
   EXPECT_NO_THROW({ snmpbulkwalk_usage(); });
}
