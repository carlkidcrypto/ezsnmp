#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmpwalk.h"

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;
   *response = NULL;
   return STAT_SUCCESS;
}

class SnmpWalkNullShimTest : public ::testing::Test {};

TEST_F(SnmpWalkNullShimTest, TestNullResponseThrowsPacketError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpwalk(args, "testing_walk_null_shim");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}

TEST_F(SnmpWalkNullShimTest, TestNullResponseWithCiFlagThrowsPacketError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Ci", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpwalk(args, "testing_walk_null_shim_ci");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}

/* -CI (DONT_GET_REQUESTED): covers the toggle in snmpwalk_optProc, and suppresses the
 * snmpwalk_snmp_get_and_print fallback so it does not call snmp_synch_response again. */
TEST_F(SnmpWalkNullShimTest, TestDontGetRequestedFlagThrowsPacketError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-CI", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpwalk(args, "testing_walk_null_shim_CI");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}

/* -Cc: covers NETSNMP_DS_WALK_DONT_CHECK_LEXICOGRAPHIC toggle in snmpwalk_optProc. */
TEST_F(SnmpWalkNullShimTest, TestDontCheckLexicographicFlagThrowsPacketError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cc", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpwalk(args, "testing_walk_null_shim_Cc");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}

/* Unknown -C sub-flag: snmpwalk_optProc default case throws ParseErrorBase. */
TEST_F(SnmpWalkNullShimTest, TestUnknownCFlagThrowsParseError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-CZ", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpwalk(args, "testing_walk_null_shim_unknown_cflag");
          } catch (ParseErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("Unknown flag") != std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}

/* -h triggers NETSNMP_PARSE_ARGS_SUCCESS_EXIT inside snmp_parse_args, which the
 * patched snmpwalk() converts to a ParseErrorBase throw. */
TEST_F(SnmpWalkNullShimTest, TestHelpFlagThrowsParseErrorForSuccessExit) {
   std::vector<std::string> args = {"-h"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpwalk(args, "testing_walk_null_shim_help");
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
