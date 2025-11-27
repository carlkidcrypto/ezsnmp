#include <gtest/gtest.h>

#include "datatypes.h"
#include "exceptionsbase.h"
#include "snmpgetnext.h"

class SnmpGetNextTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SnmpGetNextTest, TestMissingOid) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpgetnext(args, "testing");
          } catch (GenericErrorBase const& e) {
             EXPECT_STREQ("Missing object name\n", e.what());
             throw;
          }
       },
       GenericErrorBase);
}

TEST_F(SnmpGetNextTest, TestTooManyOids) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161"};

   // Add more OIDs than SNMP_MAX_CMDLINE_OIDS (128)
   for (int i = 0; i < 129; i++) {
      args.push_back("SNMPv2-MIB::sysLocation.0");
   }

   EXPECT_THROW(
       {
          try {
             auto results = snmpgetnext(args, "testing");
          } catch (GenericErrorBase const& e) {
             EXPECT_STREQ(
                 "Too many object identifiers specified. Only 128 allowed in one request.\n",
                 e.what());
             throw;
          }
       },
       GenericErrorBase);
}

TEST_F(SnmpGetNextTest, TestInvalidOid) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "INVALID-MIB::nonexistent.0"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpgetnext(args, "testing");
          } catch (GenericErrorBase const& e) {
             EXPECT_STREQ(e.what(), "INVALID-MIB::nonexistent.0: Unknown Object Identifier");
             throw;
          }
       },
       GenericErrorBase);
}

TEST_F(SnmpGetNextTest, TestUnknownHost) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "nonexistenthost:11161", "SNMPv2-MIB::sysLocation.0"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpgetnext(args, "testing");
          } catch (ConnectionErrorBase const& e) {
             // Check that error message contains key parts (may vary by platform)
             std::string error_msg(e.what());
             EXPECT_TRUE(error_msg.find("snmpgetnext") != std::string::npos);
             EXPECT_TRUE(error_msg.find("Unknown host") != std::string::npos);
             EXPECT_TRUE(error_msg.find("nonexistenthost:11161") != std::string::npos);
             throw;
          }
       },
       ConnectionErrorBase);
}

TEST_F(SnmpGetNextTest, TestInvalidVersion) {
   std::vector<std::string> args = {
       "-v", "999", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysLocation.0"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpgetnext(args, "testing");
          } catch (ParseErrorBase const& e) {
             EXPECT_STREQ(e.what(), "NETSNMP_PARSE_ARGS_ERROR_USAGE");
             throw;
          }
       },
       ParseErrorBase);
}
