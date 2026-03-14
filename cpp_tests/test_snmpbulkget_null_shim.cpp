#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmpbulkget.h"

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;
   *response = NULL;
   return STAT_SUCCESS;
}

class SnmpBulkGetNullShimTest : public ::testing::Test {};

TEST_F(SnmpBulkGetNullShimTest, TestNullResponseThrowsPacketError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkget(args, "testing_bulkget_null_shim");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}

/* -Cn2: covers the non-repeaters numeric parsing branch in snmpbulkget_optProc. */
TEST_F(SnmpBulkGetNullShimTest, TestNonRepeatersFlagCoversNumericParsing) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cn2", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkget(args, "testing_bulkget_null_shim_cn");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}

/* -Cr5: covers the max-repeaters numeric parsing branch in snmpbulkget_optProc. */
TEST_F(SnmpBulkGetNullShimTest, TestMaxRepeatersFlagCoversNumericParsing) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cr5", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkget(args, "testing_bulkget_null_shim_cr");
          } catch (PacketErrorBase const &e) {
             EXPECT_STREQ(e.what(), "received NULL response from snmp_synch_response");
             throw;
          }
       },
       PacketErrorBase);
}

/* Unknown -C sub-flag: snmpbulkget_optProc default case throws ParseErrorBase. */
TEST_F(SnmpBulkGetNullShimTest, TestUnknownCFlagThrowsParseError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-CZ", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkget(args, "testing_bulkget_null_shim_unknown_cflag");
          } catch (ParseErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("Unknown flag") != std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}
