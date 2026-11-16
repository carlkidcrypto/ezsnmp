#include <gtest/gtest.h>

#include "exceptionsbase.h"
#include "snmpstatus.h"

class SnmpStatusTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SnmpStatusTest, TestHelpThrowsParseError) {
   std::vector<std::string> args = {"-h"};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_help"), ParseErrorBase);
}

TEST_F(SnmpStatusTest, TestVersionThrowsParseError) {
   std::vector<std::string> args = {"-V"};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_version"), ParseErrorBase);
}

TEST_F(SnmpStatusTest, TestEmptyArgsThrowsParseError) {
   std::vector<std::string> args = {};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_empty"), ParseErrorBase);
}

TEST_F(SnmpStatusTest, TestInvalidOptionThrowsParseError) {
   std::vector<std::string> args = {"-Z", "localhost:11161"};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_invalid_opt"), ParseErrorBase);
}

TEST_F(SnmpStatusTest, TestInvalidCOptionThrowsParseError) {
   std::vector<std::string> args = {"-CX", "-v", "2c", "-c", "public", "localhost:11161"};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_invalid_c"), ParseErrorBase);
}

TEST_F(SnmpStatusTest, TestTimeoutOnUnreachableHost) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public",         "-t",
                                    "1",  "-r", "0",  "127.0.0.1:19999"};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_timeout"), TimeoutErrorBase);
}

TEST_F(SnmpStatusTest, TestDontFixPdusOptionAcceptedBeforeTimeout) {
   std::vector<std::string> args = {"-Cf", "-v", "2c", "-c", "public",
                                    "-t",  "1",  "-r", "0",  "127.0.0.1:19999"};
   EXPECT_THROW(snmpstatus(args, "testing_snmpstatus_cf_timeout"), TimeoutErrorBase);
}
