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
   EXPECT_THROW(
       {
          try {
             snmptrap(args, "testing_snmptrap_unknown_host");
          } catch (ConnectionErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("snmptrap") != std::string::npos);
             throw;
          }
       },
       ConnectionErrorBase);
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
