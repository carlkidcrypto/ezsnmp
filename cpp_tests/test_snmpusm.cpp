#include <gtest/gtest.h>

#include "exceptionsbase.h"
#include "snmpusm.h"

class SnmpUsmTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SnmpUsmTest, TestHelpThrowsParseError) {
   std::vector<std::string> args = {"-h"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_help"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestVersionThrowsParseError) {
   std::vector<std::string> args = {"-V"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_version"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestInvalidOptionThrowsParseError) {
   std::vector<std::string> args = {"-Z", "localhost", "delete", "testuser"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_invalid_opt"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestInvalidCFlagThrowsParseError) {
   std::vector<std::string> args = {"-CX",    "-v",        "2c",     "-c",
                                    "public", "localhost", "delete", "testuser"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_invalid_c_flag"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestBadCpOptionNoArgThrowsParseError) {
   std::vector<std::string> args = {"-Cp"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_bad_cp"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestBadCeOptionNoArgThrowsParseError) {
   std::vector<std::string> args = {"-CE"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_bad_ce_no_arg"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestBadCeOptionInvalidHexThrowsParseError) {
   std::vector<std::string> args = {"-CE",    "ZZZZ",      "-v",     "2c",      "-c",
                                    "public", "localhost", "delete", "testuser"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_bad_ce_hex"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestMissingOperationThrowsParseError) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_missing_op"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestUnknownCommandThrowsParseError) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost", "invalidcmd"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_unknown_cmd"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestCreateMissingUserThrowsParseError) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost", "create"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_create_missing_user"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestDeleteMissingUserThrowsParseError) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost", "delete"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_delete_missing_user"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestActivateMissingUserThrowsParseError) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost", "activate"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_activate_missing_user"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestDeactivateMissingUserThrowsParseError) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost", "deactivate"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_deactivate_missing_user"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestCloneFromMissingUserThrowsParseError) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost", "cloneFrom"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_clonefrom_missing_user"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestCloneFromMissingSourceUserThrowsParseError) {
   std::vector<std::string> args = {"-v",        "2c",        "-c",     "public",
                                    "localhost", "cloneFrom", "newuser"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_clonefrom_missing_src"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestPasswdShortNewPassThrowsParseError) {
   std::vector<std::string> args = {"-v",        "2c",     "-c",         "public",
                                    "localhost", "passwd", "oldpass123", "short"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_passwd_short_new"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestPasswdShortOldPassThrowsParseError) {
   std::vector<std::string> args = {"-v",        "2c",     "-c",    "public",
                                    "localhost", "passwd", "short", "newpass123"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_passwd_short_old"), ParseErrorBase);
}

TEST_F(SnmpUsmTest, TestUnreachableHostTimesOutOrErrors) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-r", "0", "-t", "1", "127.0.0.1:19999", "delete", "testuser"};
   EXPECT_THROW(snmpusm(args, "testing_snmpusm_timeout"), TimeoutErrorBase);
}
