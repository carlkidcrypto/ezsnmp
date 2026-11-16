#include <gtest/gtest.h>

#include <cstdlib>
#include <string>
#include <vector>

#include "exceptionsbase.h"
#include "snmpdf.h"

namespace {

bool is_test_snmpd_available() {
   return std::system(
              "snmpget -v2c -c public -t 1 -r 0 udp:127.0.0.1:11161 "
              ".1.3.6.1.2.1.1.1.0 >/dev/null 2>&1") == 0;
}

} // namespace

class SnmpDfTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SnmpDfTest, TestInvalidCOptionThrowsParseError) {
   std::vector<std::string> args = {"-CZ", "-v", "2c", "-c", "public", "localhost:11161"};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_invalid_c"), ParseErrorBase);
}

TEST_F(SnmpDfTest, TestInvalidOptionThrowsParseError) {
   std::vector<std::string> args = {"-Z", "-v", "2c", "-c", "public", "localhost:11161"};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_invalid_opt"), ParseErrorBase);
}

TEST_F(SnmpDfTest, TestHelpThrowsParseError) {
   std::vector<std::string> args = {"-h"};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_help"), ParseErrorBase);
}

TEST_F(SnmpDfTest, TestVersionThrowsParseError) {
   std::vector<std::string> args = {"-V"};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_version"), ParseErrorBase);
}

TEST_F(SnmpDfTest, TestMissingHostThrowsParseError) {
   std::vector<std::string> args = {};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_missing_host"), ParseErrorBase);
}

TEST_F(SnmpDfTest, TestExtraArgumentThrowsParseError) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161", "extra_arg"};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_extra_arg"), ParseErrorBase);
}

TEST_F(SnmpDfTest, TestTimeoutThrowsTimeoutError) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public",         "-t",
                                    "1",  "-r", "0",  "127.0.0.1:19999"};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_timeout"), TimeoutErrorBase);
}

TEST_F(SnmpDfTest, TestInvalidHostnameThrows) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-t", "1", "-r", "0", "nonexistent.invalid.host.example:161"};
   EXPECT_THROW(snmpdf(args, "testing_snmpdf_bad_host"), GenericErrorBase);
}

TEST_F(SnmpDfTest, TestLiveSnmpdfDefault) {
   if (!is_test_snmpd_available()) {
      GTEST_SKIP() << "Test snmpd not running on 127.0.0.1:11161";
   }
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161"};
   auto result = snmpdf(args, "testing_snmpdf_default");
   ASSERT_GE(result.size(), 2u);
   EXPECT_NE(result[0].find("Description"), std::string::npos);
   EXPECT_NE(result[0].find("Size (kB)"), std::string::npos);
   EXPECT_NE(result[0].find("Used%"), std::string::npos);
}

TEST_F(SnmpDfTest, TestLiveSnmpdfHumanBinary) {
   if (!is_test_snmpd_available()) {
      GTEST_SKIP() << "Test snmpd not running on 127.0.0.1:11161";
   }
   std::vector<std::string> args = {"-Ch", "-v", "2c", "-c", "public", "localhost:11161"};
   auto result = snmpdf(args, "testing_snmpdf_human_binary");
   ASSERT_GE(result.size(), 2u);
   EXPECT_NE(result[0].find("Description"), std::string::npos);
   EXPECT_NE(result[0].find("Size"), std::string::npos);
   EXPECT_EQ(result[0].find("Size (kB)"), std::string::npos);
}

TEST_F(SnmpDfTest, TestLiveSnmpdfHumanSI) {
   if (!is_test_snmpd_available()) {
      GTEST_SKIP() << "Test snmpd not running on 127.0.0.1:11161";
   }
   std::vector<std::string> args = {"-CH", "-v", "2c", "-c", "public", "localhost:11161"};
   auto result = snmpdf(args, "testing_snmpdf_human_si");
   ASSERT_GE(result.size(), 2u);
   EXPECT_NE(result[0].find("Description"), std::string::npos);
   EXPECT_NE(result[0].find("Size"), std::string::npos);
}
