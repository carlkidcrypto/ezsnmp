/* Shim-test for snmp_perror_exception().
 *
 * snmp_perror_exception() reads the global snmp_errno and calls
 * snmp_api_errstring() to obtain a human-readable error string, then always
 * throws GenericErrorBase.  We stub snmp_api_errstring() to return a
 * controlled message and verify:
 *   1. The function always throws GenericErrorBase.
 *   2. The thrown message contains the prog_string argument.
 *   3. The thrown message contains the stubbed api error string.
 */

#include <gtest/gtest.h>

#include <string>

#include "exceptionsbase.h"
#include "helpers.h"

static std::string g_api_error_string = "stubbed api error";

extern "C" char const *snmp_api_errstring(int /*snmp_errnumber*/) {
   return g_api_error_string.c_str();
}

class HelpersSnmpPerrorShimTest : public ::testing::Test {
  protected:
   void SetUp() override { g_api_error_string = "stubbed api error"; }
   void TearDown() override { g_api_error_string = "stubbed api error"; }
};

TEST_F(HelpersSnmpPerrorShimTest, ThrowsGenericErrorBase) {
   EXPECT_THROW(snmp_perror_exception("test_prog"), GenericErrorBase);
}

TEST_F(HelpersSnmpPerrorShimTest, ErrorMessageContainsProgramString) {
   try {
      snmp_perror_exception("my_program");
      FAIL() << "Expected GenericErrorBase to be thrown";
   } catch (GenericErrorBase const &e) {
      std::string msg(e.what());
      EXPECT_NE(msg.find("my_program"), std::string::npos)
          << "Message should contain prog_string, got: " << msg;
   }
}

TEST_F(HelpersSnmpPerrorShimTest, ErrorMessageContainsApiErrorString) {
   g_api_error_string = "custom api error text";
   try {
      snmp_perror_exception("prog");
      FAIL() << "Expected GenericErrorBase to be thrown";
   } catch (GenericErrorBase const &e) {
      std::string msg(e.what());
      EXPECT_NE(msg.find("custom api error text"), std::string::npos)
          << "Message should contain api error string, got: " << msg;
   }
}

TEST_F(HelpersSnmpPerrorShimTest, MessageFormatIsProgStringColonError) {
   g_api_error_string = "error detail";
   try {
      snmp_perror_exception("snmpget");
      FAIL() << "Expected GenericErrorBase to be thrown";
   } catch (GenericErrorBase const &e) {
      std::string msg(e.what());
      // Expected format: "snmpget: error detail"
      EXPECT_NE(msg.find("snmpget: error detail"), std::string::npos)
          << "Message format should be 'prog: error', got: " << msg;
   }
}
