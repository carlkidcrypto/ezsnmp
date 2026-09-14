#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "datatypes.h"
#include "exceptionsbase.h"
#include "snmpset.h"

extern "C" int snmp_sess_synch_response(void *sessp, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)sessp;
   (void)pdu;
   *response = NULL;
   return STAT_SUCCESS;
}

class SnmpSetNullShimTest : public ::testing::Test {};

TEST_F(SnmpSetNullShimTest, TestNullResponseThrowsPacketError) {
   std::vector<std::string> args = {
       "-v", "2c",           "-c", "public", "localhost:11161", "SNMPv2-MIB::sysLocation.0",
       "s",  "test_location"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpset(args, "testing_set_null_shim");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_sess_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}

/* -h triggers NETSNMP_PARSE_ARGS_SUCCESS_EXIT path in snmpset(). */
TEST_F(SnmpSetNullShimTest, TestHelpFlagThrowsParseErrorForSuccessExit) {
   std::vector<std::string> args = {"-h"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpset(args, "testing_set_null_shim_help");
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

/* Net-SNMP rejects an invocation without an object name before snmpset validation. */
TEST_F(SnmpSetNullShimTest, TestMissingObjectNameThrowsParseError) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161"};

   EXPECT_THROW(snmpset(args, "testing_set_null_shim_missing_obj"), ParseErrorBase);
}

/* Net-SNMP rejects oversized malformed assignments during option parsing. */
TEST_F(SnmpSetNullShimTest, TestTooManyAssignmentsThrowsParseError) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161"};

   for (int i = 0; i < (3 * SNMP_MAX_CMDLINE_OIDS) + 1; ++i) {
      args.push_back("dummy");
   }

   EXPECT_THROW(snmpset(args, "testing_set_null_shim_too_many_assignments"), ParseErrorBase);
}
