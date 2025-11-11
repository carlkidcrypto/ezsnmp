#include <gtest/gtest.h>

#include "exceptionsbase.h"
#include "snmpget.h"

class SnmpGetTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SnmpGetTest, TestBasicGet) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysLocation.0"};

   auto results = snmpget(args, "testing");
   ASSERT_EQ(results.size(), 1);
   EXPECT_EQ(results[0]._to_string(),
             "oid: SNMPv2-MIB::sysLocation, index: 0, type: STRING, value: my original location, converted_value: my original location");
}

TEST_F(SnmpGetTest, TestMultipleOids) {
   std::vector<std::string> args = {"-v",
                                    "2c",
                                    "-c",
                                    "public",
                                    "localhost:11161",
                                    "SNMPv2-MIB::sysLocation.0",
                                    "ifAdminStatus.1"};

   auto results = snmpget(args, "testing");
   ASSERT_EQ(results.size(), 2);
   EXPECT_EQ(results[0]._to_string(),
             "oid: SNMPv2-MIB::sysLocation, index: 0, type: STRING, value: my original location, converted_value: my original location");
   EXPECT_EQ(results[1]._to_string(),
             "oid: IF-MIB::ifAdminStatus, index: 1, type: INTEGER, value: up(1), converted_value: 1");
}

TEST_F(SnmpGetTest, TestV3Get) {
   std::vector<std::string> args = {"-v",
                                    "3",
                                    "-u",
                                    "secondary_sha_aes",
                                    "-l",
                                    "authPriv",
                                    "-a",
                                    "SHA",
                                    "-A",
                                    "auth_second",
                                    "-x",
                                    "AES",
                                    "-X",
                                    "priv_second",
                                    "localhost:11161",
                                    "SNMPv2-MIB::sysLocation.0"};

   auto results = snmpget(args, "testing");
   ASSERT_EQ(results.size(), 1);
   EXPECT_EQ(results[0]._to_string(),
             "oid: SNMPv2-MIB::sysLocation, index: 0, type: STRING, value: my original location, converted_value: my original location");
}

TEST_F(SnmpGetTest, TestMissingOid) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpget(args, "testing");
          } catch (GenericErrorBase const& e) {
             EXPECT_STREQ("Missing object name\n", e.what());
             throw;
          }
       },
       GenericErrorBase);
}

TEST_F(SnmpGetTest, TestTooManyOids) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161"};

   // Add more OIDs than SNMP_MAX_CMDLINE_OIDS (128)
   for (int i = 0; i < 129; i++) {
      args.push_back("SNMPv2-MIB::sysLocation.0");
   }

   EXPECT_THROW(
       {
          try {
             auto results = snmpget(args, "testing");
          } catch (GenericErrorBase const& e) {
             EXPECT_STREQ(
                 "Too many object identifiers specified. Only 128 allowed in one request.\n",
                 e.what());
             throw;
          }
       },
       GenericErrorBase);
}

TEST_F(SnmpGetTest, TestInvalidOid) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "INVALID-MIB::nonexistent.0"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpget(args, "testing");
          } catch (GenericErrorBase const& e) {
             // Error message may vary by platform, just check it contains key parts
             std::string error_msg(e.what());
             EXPECT_TRUE(error_msg.find("INVALID-MIB::nonexistent.0") != std::string::npos);
             EXPECT_TRUE(error_msg.find("Unknown Object Identifier") != std::string::npos);
             throw;
          }
       },
       GenericErrorBase);
}

TEST_F(SnmpGetTest, TestUknownHost) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "nonexistenthost:11161", "SNMPv2-MIB::sysLocation.0"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpget(args, "testing");
          } catch (ConnectionErrorBase const& e) {
             // Error message may vary by platform, just check it contains key parts
             std::string error_msg(e.what());
             EXPECT_TRUE(error_msg.find("snmpget") != std::string::npos);
             EXPECT_TRUE(error_msg.find("Unknown host") != std::string::npos);
             EXPECT_TRUE(error_msg.find("nonexistenthost:11161") != std::string::npos);
             throw;
          }
       },
       ConnectionErrorBase);
}

TEST_F(SnmpGetTest, TestInvalidVersion) {
   std::vector<std::string> args = {
       "-v", "999", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysLocation.0"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpget(args, "testing");
          } catch (ParseErrorBase const& e) {
             EXPECT_STREQ(e.what(), "NETSNMP_PARSE_ARGS_ERROR_USAGE");
             throw;
          }
       },
       ParseErrorBase);
}

TEST_F(SnmpGetTest, TestRepeatedOidGetWithSameFlag) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-O", "e", "localhost:11161", "IF-MIB::ifAdminStatus.1"};

   std::string expected_result = "oid: IF-MIB::ifAdminStatus, index: 1, type: INTEGER, value: 1, converted_value: 1";

   for (int i = 0; i < 5; ++i) {
      auto results = snmpget(args, "testing");
      EXPECT_EQ(results.size(), 1);
      EXPECT_EQ(results[0]._to_string(), expected_result);
   }
}

TEST_F(SnmpGetTest, TestRepeatedOidGetWithEnumsAndWithout) {
   std::vector<std::string> base_args = {
       "-v", "2c", "-c", "public", "localhost:11161", "IF-MIB::ifAdminStatus.1"};

   std::string expected_result_enum =
       "oid: IF-MIB::ifAdminStatus, index: 1, type: INTEGER, value: 1, converted_value: 1";
   std::string expected_result_no_enum =
       "oid: IF-MIB::ifAdminStatus, index: 1, type: INTEGER, value: up(1), converted_value: 1";

   for (int i = 0; i < 2; ++i) {
      std::vector<std::string> args = base_args;

      if (i % 2 == 0) {
         args.insert(args.begin() + 2, "-O");
         args.insert(args.begin() + 3, "e");
      }

      auto results = snmpget(args, "testing");
      EXPECT_EQ(results.size(), 1);

      if (i % 2 == 0) {
         EXPECT_EQ(results[0]._to_string(), expected_result_enum);
      } else {
         EXPECT_EQ(results[0]._to_string(), expected_result_no_enum);
      }
   }
}
