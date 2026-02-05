#include <gtest/gtest.h>

#include "datatypes.h"
#include "exceptionsbase.h"
#include "snmpset.h"

class SnmpSetTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SnmpSetTest, TestInvalidOid) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "INVALID-MIB::nonexistent.0", "s", "test"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpset(args, "testing");
          } catch (GenericErrorBase const& e) {
             EXPECT_STREQ(e.what(), "INVALID-MIB::nonexistent.0: Unknown Object Identifier");
             throw;
          }
       },
       GenericErrorBase);
}

TEST_F(SnmpSetTest, TestUnknownHost) {
   std::vector<std::string> args = {
       "-v", "2c",  "-c", "public", "nonexistenthost:11161", "SNMPv2-MIB::sysLocation.0",
       "s",  "test"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpset(args, "testing");
          } catch (ConnectionErrorBase const& e) {
             // Check for host-related errors - message varies by platform
             std::string error_msg(e.what());
             EXPECT_TRUE(error_msg.find("snmpset") != std::string::npos);
             bool is_host_error = 
                 error_msg.find("Unknown host") != std::string::npos ||
                 error_msg.find("Invalid address") != std::string::npos ||
                 error_msg.find("Name or service") != std::string::npos ||
                 error_msg.find("No address associated") != std::string::npos ||
                 error_msg.find("Name resolution") != std::string::npos;
             EXPECT_TRUE(is_host_error);
             EXPECT_TRUE(error_msg.find("nonexistenthost") != std::string::npos);
             throw;
          }
       },
       ConnectionErrorBase);
}

TEST_F(SnmpSetTest, TestInvalidVersion) {
   std::vector<std::string> args = {
       "-v", "999", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysLocation.0", "s", "test"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpset(args, "testing");
          } catch (ParseErrorBase const& e) {
             EXPECT_STREQ(e.what(), "NETSNMP_PARSE_ARGS_ERROR_USAGE");
             throw;
          }
       },
       ParseErrorBase);
}

// Test -Cq option (quiet mode)
TEST_F(SnmpSetTest, TestQuietOption) {
   std::vector<std::string> args = {
       "-v", "2c",        "-c", "public", "-Cq", "localhost:11161", "SNMPv2-MIB::sysLocation.0",
       "s",  "test quiet"};

   // Quiet mode should return empty results on success
   auto results = snmpset(args, "testing");
   EXPECT_TRUE(results.empty());
}

// Test unknown -C option
TEST_F(SnmpSetTest, TestUnknownCOption) {
   std::vector<std::string> args = {
       "-v", "2c",  "-c", "public", "-Cz", "localhost:11161", "SNMPv2-MIB::sysLocation.0",
       "s",  "test"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpset(args, "testing");
          } catch (ParseErrorBase const& e) {
             EXPECT_TRUE(std::string(e.what()).find("Unknown flag passed to -C: z") !=
                         std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}

// Test successful set operation
TEST_F(SnmpSetTest, TestSuccessfulSet) {
   std::vector<std::string> args = {
       "-v", "2c",           "-c", "public", "localhost:11161", "SNMPv2-MIB::sysLocation.0",
       "s",  "test location"};

   auto results = snmpset(args, "testing_set");
   ASSERT_FALSE(results.empty());
   EXPECT_TRUE(results[0].value.find("test location") != std::string::npos);

   // Reset to original
   std::vector<std::string> reset_args = {"-v",
                                          "2c",
                                          "-c",
                                          "public",
                                          "localhost:11161",
                                          "SNMPv2-MIB::sysLocation.0",
                                          "s",
                                          "my original location"};
   snmpset(reset_args, "testing_reset");
}
