#include <gtest/gtest.h>

#include "datatypes.h"
#include "exceptionsbase.h"
#include "snmpbulkget.h"

class SnmpBulkGetTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SnmpBulkGetTest, TestInvalidOid) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "INVALID-MIB::nonexistent"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkget(args, "testing");
          } catch (GenericErrorBase const& e) {
             EXPECT_STREQ(e.what(), "INVALID-MIB::nonexistent: Unknown Object Identifier");
             throw;
          }
       },
       GenericErrorBase);
}

TEST_F(SnmpBulkGetTest, TestUnknownHost) {
   std::vector<std::string> args = {"-v",           "2c", "-c", "public", "nonexistenthost:11161",
                                    "1.3.6.1.2.1.1"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkget(args, "testing");
          } catch (GenericErrorBase const& e) {
             // Check that error is thrown (may be connection or OID error)
             std::string error_msg(e.what());
             EXPECT_FALSE(error_msg.empty());
             throw;
          }
       },
       GenericErrorBase);
}

TEST_F(SnmpBulkGetTest, TestInvalidVersion) {
   std::vector<std::string> args = {
       "-v", "999", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkget(args, "testing");
          } catch (ParseErrorBase const& e) {
             EXPECT_STREQ(e.what(), "NETSNMP_PARSE_ARGS_ERROR_USAGE");
             throw;
          }
       },
       ParseErrorBase);
}

// Test -Cn option (non-repeaters)
TEST_F(SnmpBulkGetTest, TestNonRepeatersOption) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cn1", "localhost:11161", "SNMPv2-MIB::sysDescr.0", "SNMPv2-MIB::sysORDescr"};

   auto results = snmpbulkget(args, "testing");
   EXPECT_FALSE(results.empty());
}

// Test -Cr option (max-repeaters)
TEST_F(SnmpBulkGetTest, TestMaxRepeatersOption) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cr5", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   auto results = snmpbulkget(args, "testing_cr");
   EXPECT_FALSE(results.empty());
}

// Test unknown -C option
TEST_F(SnmpBulkGetTest, TestUnknownCOption) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-Cz", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkget(args, "testing");
          } catch (ParseErrorBase const& e) {
             EXPECT_TRUE(std::string(e.what()).find("Unknown flag passed to -C: z") !=
                         std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}

// Test valid bulkget - This should be first test that runs
TEST_F(SnmpBulkGetTest, TestBasicBulkGet) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   auto results = snmpbulkget(args, "testing_basic");
   EXPECT_FALSE(results.empty());
}
