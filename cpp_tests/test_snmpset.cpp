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
   std::vector<std::string> args = {"-v",
                                    "2c",
                                    "-c",
                                    "public",
                                    "nonexistenthost:11161",
                                    "SNMPv2-MIB::sysLocation.0",
                                    "s",
                                    "test"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpset(args, "testing");
          } catch (ConnectionErrorBase const& e) {
             // Check that error message contains key parts (may vary by platform)
             std::string error_msg(e.what());
             EXPECT_TRUE(error_msg.find("snmpset") != std::string::npos);
             EXPECT_TRUE(error_msg.find("Unknown host") != std::string::npos);
             EXPECT_TRUE(error_msg.find("nonexistenthost:11161") != std::string::npos);
             throw;
          }
       },
       ConnectionErrorBase);
}

TEST_F(SnmpSetTest, TestInvalidVersion) {
   std::vector<std::string> args = {"-v",
                                    "999",
                                    "-c",
                                    "public",
                                    "localhost:11161",
                                    "SNMPv2-MIB::sysLocation.0",
                                    "s",
                                    "test"};

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


