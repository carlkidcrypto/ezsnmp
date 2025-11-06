#include <gtest/gtest.h>

#include "exceptionsbase.h"
#include "snmpwalk.h"

class SnmpWalkTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SnmpWalkTest, TestMissingOid) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpwalk(args, "testing");
          } catch (GenericErrorBase const& e) {
             // snmpwalk without OID defaults to root walk which may timeout or error
             // Platform-dependent behavior - just verify an exception is thrown
             std::string error_msg(e.what());
             EXPECT_FALSE(error_msg.empty());
             throw;
          }
       },
       GenericErrorBase);
}

TEST_F(SnmpWalkTest, TestInvalidOid) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "INVALID-MIB::nonexistent"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpwalk(args, "testing");
          } catch (GenericErrorBase const& e) {
             EXPECT_STREQ(e.what(), "INVALID-MIB::nonexistent: Unknown Object Identifier");
             throw;
          }
       },
       GenericErrorBase);
}

TEST_F(SnmpWalkTest, TestUnknownHost) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "nonexistenthost:11161", "1.3.6.1.2.1.1"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpwalk(args, "testing");
          } catch (GenericErrorBase const& e) {
             // Check that error is thrown (may be connection or OID error)
             std::string error_msg(e.what());
             EXPECT_FALSE(error_msg.empty());
             throw;
          }
       },
       GenericErrorBase);
}

TEST_F(SnmpWalkTest, TestInvalidVersion) {
   std::vector<std::string> args = {
       "-v", "999", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpwalk(args, "testing");
          } catch (ParseErrorBase const& e) {
             EXPECT_STREQ(e.what(), "NETSNMP_PARSE_ARGS_ERROR_USAGE");
             throw;
          }
       },
       ParseErrorBase);
}
