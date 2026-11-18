#include <gtest/gtest.h>

#include "exceptionsbase.h"
#include "snmptable.h"

class SnmpTableTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SnmpTableTest, TestHelpThrowsParseError) {
   std::vector<std::string> args = {"-h"};
   EXPECT_THROW(snmptable(args, "testing_snmptable_help"), ParseErrorBase);
}

TEST_F(SnmpTableTest, TestVersionThrowsParseError) {
   std::vector<std::string> args = {"-V"};
   EXPECT_THROW(snmptable(args, "testing_snmptable_version"), ParseErrorBase);
}

TEST_F(SnmpTableTest, TestConfigHelpThrowsParseError) {
   std::vector<std::string> args = {"-H"};
   EXPECT_THROW(snmptable(args, "testing_snmptable_config_help"), ParseErrorBase);
}

TEST_F(SnmpTableTest, TestMissingTableNameThrowsParseError) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost"};
   EXPECT_THROW(snmptable(args, "testing_snmptable_missing_oid"), ParseErrorBase);
}

TEST_F(SnmpTableTest, TestTooManyArgsThrowsParseError) {
   std::vector<std::string> args = {"-v",   "2c", "-c", "public", "localhost", "IF-MIB::ifTable",
                                    "extra"};
   EXPECT_THROW(snmptable(args, "testing_snmptable_extra_arg"), ParseErrorBase);
}

TEST_F(SnmpTableTest, TestInvalidCOptionThrowsParseError) {
   std::vector<std::string> args = {
       "-CZ", "-v", "2c", "-c", "public", "localhost", "IF-MIB::ifTable"};
   EXPECT_THROW(snmptable(args, "testing_snmptable_invalid_c"), ParseErrorBase);
}

TEST_F(SnmpTableTest, TestInvalidCwZeroThrowsParseError) {
   std::vector<std::string> args = {"-Cw", "0",      "-v",        "2c",
                                    "-c",  "public", "localhost", "IF-MIB::ifTable"};
   EXPECT_THROW(snmptable(args, "testing_snmptable_invalid_cw"), ParseErrorBase);
}

TEST_F(SnmpTableTest, TestMissingCwArgThrowsParseError) {
   std::vector<std::string> args = {"-Cw"};
   EXPECT_THROW(snmptable(args, "testing_snmptable_missing_cw"), ParseErrorBase);
}

TEST_F(SnmpTableTest, TestInvalidCcTooSmallThrowsParseError) {
   std::vector<std::string> args = {"-Cc", "2",      "-v",        "2c",
                                    "-c",  "public", "localhost", "IF-MIB::ifTable"};
   EXPECT_THROW(snmptable(args, "testing_snmptable_invalid_cc"), ParseErrorBase);
}

TEST_F(SnmpTableTest, TestMissingCcArgThrowsParseError) {
   std::vector<std::string> args = {"-Cc"};
   EXPECT_THROW(snmptable(args, "testing_snmptable_missing_cc"), ParseErrorBase);
}

TEST_F(SnmpTableTest, TestMissingCfArgThrowsParseError) {
   std::vector<std::string> args = {"-Cf"};
   EXPECT_THROW(snmptable(args, "testing_snmptable_missing_cf"), ParseErrorBase);
}

TEST_F(SnmpTableTest, TestInvalidCrZeroThrowsParseError) {
   std::vector<std::string> args = {"-Cr", "0",      "-v",        "2c",
                                    "-c",  "public", "localhost", "IF-MIB::ifTable"};
   EXPECT_THROW(snmptable(args, "testing_snmptable_invalid_cr"), ParseErrorBase);
}

TEST_F(SnmpTableTest, TestMissingCrArgThrowsParseError) {
   std::vector<std::string> args = {"-Cr"};
   EXPECT_THROW(snmptable(args, "testing_snmptable_missing_cr"), ParseErrorBase);
}

TEST_F(SnmpTableTest, TestUnknownOidThrowsGenericError) {
   std::vector<std::string> args = {"-v",     "2c",        "-c",
                                    "public", "localhost", "NONEXISTENT-MIB::doesNotExist"};
   EXPECT_THROW(snmptable(args, "testing_snmptable_unknown_oid"), GenericErrorBase);
}

TEST_F(SnmpTableTest, TestNonTableOidThrowsParseError) {
   std::vector<std::string> args = {"-v",     "2c",        "-c",
                                    "public", "localhost", "SNMPv2-MIB::sysDescr.0"};
   EXPECT_THROW(snmptable(args, "testing_snmptable_non_table"), ParseErrorBase);
}

TEST_F(SnmpTableTest, TestHeadersOnlyIfTable) {
   std::vector<std::string> args = {
       "-Ch", "-v", "2c", "-c", "public", "localhost:11161", "IF-MIB::ifTable"};
   auto result = snmptable(args, "testing_snmptable_headers");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_NE(result[0].find("ifIndex"), std::string::npos);
   EXPECT_NE(result[0].find("ifDescr"), std::string::npos);
}

TEST_F(SnmpTableTest, TestHeadersOnlyBriefAndDelimiter) {
   std::vector<std::string> args = {"-Ch",
                                    "-Cb",
                                    "-Ci",
                                    "-Cl",
                                    "-Cf",
                                    ",",
                                    "-v",
                                    "2c",
                                    "-c",
                                    "public",
                                    "localhost:11161",
                                    "IF-MIB::ifTable"};
   auto result = snmptable(args, "testing_snmptable_brief_delim");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_NE(result[0].find("index,"), std::string::npos);
   EXPECT_NE(result[0].find("Index"), std::string::npos);
   EXPECT_EQ(result[0].find("ifIndex"), std::string::npos);
}

TEST_F(SnmpTableTest, TestHeadersOnlyMultiPartWidth) {
   std::vector<std::string> args = {
       "-Ch", "-Cw", "40", "-v", "2c", "-c", "public", "localhost:11161", "IF-MIB::ifTable"};
   auto result = snmptable(args, "testing_snmptable_multipart");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_NE(result[0].find("part 2"), std::string::npos);
}

TEST_F(SnmpTableTest, TestHeadersOnlyColumnWidth) {
   std::vector<std::string> args = {"-Ch",
                                    "-Cc",
                                    "12",
                                    "-Cw",
                                    "30",
                                    "-v",
                                    "2c",
                                    "-c",
                                    "public",
                                    "localhost:11161",
                                    "IF-MIB::ifTable"};
   auto result = snmptable(args, "testing_snmptable_col_width");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_NE(result[0].find("ifIndex"), std::string::npos);
}
