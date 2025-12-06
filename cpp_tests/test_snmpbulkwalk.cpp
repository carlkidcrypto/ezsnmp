#include <gtest/gtest.h>

#include "datatypes.h"
#include "exceptionsbase.h"
#include "snmpbulkwalk.h"

class SnmpBulkWalkTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SnmpBulkWalkTest, TestInvalidOid) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "INVALID-MIB::nonexistent"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkwalk(args, "testing");
          } catch (GenericErrorBase const& e) {
             EXPECT_STREQ(e.what(), "INVALID-MIB::nonexistent: Unknown Object Identifier");
             throw;
          }
       },
       GenericErrorBase);
}

TEST_F(SnmpBulkWalkTest, TestUnknownHost) {
   std::vector<std::string> args = {"-v",           "2c", "-c", "public", "nonexistenthost:11161",
                                    "1.3.6.1.2.1.1"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkwalk(args, "testing");
          } catch (GenericErrorBase const& e) {
             // Check that error is thrown (may be connection or OID error)
             std::string error_msg(e.what());
             EXPECT_FALSE(error_msg.empty());
             throw;
          }
       },
       GenericErrorBase);
}

TEST_F(SnmpBulkWalkTest, TestInvalidVersion) {
   std::vector<std::string> args = {
       "-v", "999", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkwalk(args, "testing");
          } catch (ParseErrorBase const& e) {
             EXPECT_STREQ(e.what(), "NETSNMP_PARSE_ARGS_ERROR_USAGE");
             throw;
          }
       },
       ParseErrorBase);
}

// Test -Cc option (don't check lexicographic ordering)
TEST_F(SnmpBulkWalkTest, TestDontCheckLexicographicOption) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cc", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   auto results = snmpbulkwalk(args, "testing");
   EXPECT_FALSE(results.empty());
}

// Test -Ci option (include given OID)
TEST_F(SnmpBulkWalkTest, TestIncludeRequestedOption) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Ci", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   auto results = snmpbulkwalk(args, "testing");
   EXPECT_FALSE(results.empty());
}

// Test -Cn option (non-repeaters)
TEST_F(SnmpBulkWalkTest, TestNonRepeatersOption) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cn2", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   auto results = snmpbulkwalk(args, "testing");
   EXPECT_FALSE(results.empty());
}

// Test -Cp option (print statistics)
TEST_F(SnmpBulkWalkTest, TestPrintStatisticsOption) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cp", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   auto results = snmpbulkwalk(args, "testing");
   EXPECT_FALSE(results.empty());
}

// Test -Cr option (max-repeaters)
TEST_F(SnmpBulkWalkTest, TestMaxRepeatersOption) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cr5", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   auto results = snmpbulkwalk(args, "testing");
   EXPECT_FALSE(results.empty());
}

// Test unknown -C option
TEST_F(SnmpBulkWalkTest, TestUnknownCOption) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cz", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkwalk(args, "testing");
          } catch (ParseErrorBase const& e) {
             EXPECT_TRUE(std::string(e.what()).find("Unknown flag passed to -C: z") != std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}

// Test basic bulkwalk
TEST_F(SnmpBulkWalkTest, TestBasicBulkWalk) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   auto results = snmpbulkwalk(args, "testing");
   EXPECT_FALSE(results.empty());
}
