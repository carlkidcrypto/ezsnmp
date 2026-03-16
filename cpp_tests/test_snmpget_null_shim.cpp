#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmpget.h"

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;
   *response = NULL;
   return STAT_SUCCESS;
}

class SnmpGetNullShimTest : public ::testing::Test {};

TEST_F(SnmpGetNullShimTest, TestNullResponseThrowsPacketError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysLocation.0"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpget(args, "testing_get_null_shim");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}

/* -h triggers NETSNMP_PARSE_ARGS_SUCCESS_EXIT path in snmpget(). */
TEST_F(SnmpGetNullShimTest, TestHelpFlagThrowsParseErrorForSuccessExit) {
   std::vector<std::string> args = {"-h"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpget(args, "testing_get_null_shim_help");
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
