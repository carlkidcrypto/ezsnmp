#include <gtest/gtest.h>

#include "exceptionsbase.h"
#include "snmptrap.h"

class SnmpTrapTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

// V2c trap: UDP is fire-and-forget, so snmp_send succeeds even without a listening trap receiver.
TEST_F(SnmpTrapTest, TestBasicV2cTrap) {
   std::vector<std::string> args = {
       "-v",
       "2c",
       "-c",
       "public",
       "localhost:11162",
       "",                    // sysUpTime: empty uses current uptime
       ".1.3.6.1.6.3.1.1.5.1" // SNMPv2-MIB::snmpTraps.coldStart
   };
   int result = snmptrap(args, "testing_snmptrap_basic");
   EXPECT_EQ(result, 0);
}

TEST_F(SnmpTrapTest, TestUnknownHost) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "nonexistenthost.invalid:11162", "", ".1.3.6.1.6.3.1.1.5.1"};
   // DNS lookup failure may raise ConnectionErrorBase or GenericErrorBase depending on
   // OS/net-snmp version; accept either.
   EXPECT_THROW({ snmptrap(args, "testing_snmptrap_unknown_host"); }, GenericErrorBase);
}

TEST_F(SnmpTrapTest, TestInvalidVersion) {
   std::vector<std::string> args = {
       "-v", "999", "-c", "public", "localhost:11162", "", ".1.3.6.1.6.3.1.1.5.1"};
   EXPECT_THROW(
       {
          try {
             snmptrap(args, "testing_snmptrap_invalid_version");
          } catch (ParseErrorBase const &e) {
             throw;
          }
       },
       ParseErrorBase);
}

TEST_F(SnmpTrapTest, TestUnknownCFlag) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cz", "localhost:11162", "", ".1.3.6.1.6.3.1.1.5.1"};
   EXPECT_THROW(
       {
          try {
             snmptrap(args, "testing_snmptrap_unknown_cflag");
          } catch (ParseErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("Unknown flag passed to -C") != std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}

TEST_F(SnmpTrapTest, TestV2cTrapWithAdditionalVarbind) {
   std::vector<std::string> args = {
       "-v",
       "2c",
       "-c",
       "public",
       "localhost:11162",
       "",                       // sysUpTime
       ".1.3.6.1.6.3.1.1.5.4",   // SNMPv2-MIB::snmpTraps.linkUp
       "SNMPv2-MIB::sysDescr.0", // OID
       "s",                      // type: string
       "test description"        // value
   };
   int result = snmptrap(args, "testing_snmptrap_with_varbind");
   EXPECT_EQ(result, 0);
}

// SNMPv1 trap: fire-and-forget UDP, so snmp_send succeeds without a receiver.
// Exercises the #ifndef NETSNMP_DISABLE_SNMPV1 block in snmptrap.cpp.
TEST_F(SnmpTrapTest, TestBasicV1TrapDefaultEnterprise) {
   // SNMPv1 arg layout: host enterprise agent generic-trap specific-trap uptime
   // "" enterprise -> argv[arg][0]==0 branch (uses default enterprise OID)
   // "" uptime -> description==NULL||*description==0 branch (calls get_uptime())
   std::vector<std::string> args = {
       "-v",        "1", "-c", "public", "localhost:11162",
       "",          // enterprise: "" -> default OID branch
       "127.0.0.1", // agent
       "6",         // generic-trap
       "0",         // specific-trap
       "",          // uptime: "" -> get_uptime() branch
   };
   int result = snmptrap(args, "testing_snmptrap_v1_default_enterprise");
   EXPECT_EQ(result, 0);
}

TEST_F(SnmpTrapTest, TestBasicV1TrapExplicitUptime) {
   // non-empty uptime -> pdu->time = atol(description) branch
   std::vector<std::string> args = {
       "-v",        "1", "-c", "public", "localhost:11162",
       "",          // enterprise: default
       "127.0.0.1", // agent
       "6",         // generic-trap
       "0",         // specific-trap
       "9000",      // explicit uptime -> atol branch
   };
   int result = snmptrap(args, "testing_snmptrap_v1_explicit_uptime");
   EXPECT_EQ(result, 0);
}

TEST_F(SnmpTrapTest, TestV1TrapWithNamedEnterpriseOid) {
   // non-empty enterprise -> snmp_parse_oid branch (argv[arg][0] != 0)
   std::vector<std::string> args = {
       "-v",
       "1",
       "-c",
       "public",
       "localhost:11162",
       ".1.3.6.1.4.1", // enterprise: named OID -> OID-parse branch
       "127.0.0.1",    // agent
       "6",            // generic-trap
       "0",            // specific-trap
       "",             // uptime
   };
   int result = snmptrap(args, "testing_snmptrap_v1_named_enterprise");
   EXPECT_EQ(result, 0);
}

TEST_F(SnmpTrapTest, TestV1InformRejected) {
   // -Ci sets inform=1; combined with -v 1 triggers early exit
   // "Cannot send INFORM as SNMPv1 PDU" -> exitval=1 (no exception)
   std::vector<std::string> args = {
       "-v",
       "1",
       "-c",
       "public",
       "-Ci", // inform flag
       "localhost:11162",
       "",
       "127.0.0.1",
       "6",
       "0",
       "",
   };
   int result = snmptrap(args, "testing_snmptrap_v1_inform_rejected");
   // Returns non-zero (exitval=1) without throwing.
   EXPECT_NE(result, 0);
}
