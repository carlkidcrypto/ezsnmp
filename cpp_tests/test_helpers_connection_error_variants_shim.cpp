/* Shim-test for connection error message variants in throw_snmp_exception_from_message().
 *
 * The is_connection_error() lambda inside throw_snmp_exception_from_message()
 * checks six different patterns joined by ||.  The existing
 * test_helpers_session_perror_shim.cpp exercises only the "unknown host"
 * branch; the remaining five patterns and the "timed out" timeout variant
 * are not exercised, leaving untaken branches in the coverage report.
 *
 * This file stubs snmp_error / snmp_close and drives
 * snmp_sess_perror_exception() with all uncovered patterns.
 */

#include <gtest/gtest.h>

#include <cstring>

#include "exceptionsbase.h"
#include "helpers.h"

static std::string g_error_message = "generic error";

extern "C" void snmp_error(netsnmp_session *session,
                           int *p_errno,
                           int *p_snmp_errno,
                           char **p_str) {
   (void)session;
   if (p_errno) {
      *p_errno = 0;
   }
   if (p_snmp_errno) {
      *p_snmp_errno = 0;
   }
   if (p_str) {
      *p_str = strdup(g_error_message.c_str());
   }
}

extern "C" int snmp_close(netsnmp_session *session) {
   (void)session;
   return 0;
}

class HelpersConnectionErrorVariantsShimTest : public ::testing::Test {
  protected:
   void SetUp() override { g_error_message = "generic error"; }
   void TearDown() override { g_error_message = "generic error"; }
};

// --- Additional ConnectionErrorBase variants ---

TEST_F(HelpersConnectionErrorVariantsShimTest, NameOrServiceNotKnown) {
   g_error_message = "Name or service not known";
   netsnmp_session session{};
   EXPECT_THROW(snmp_sess_perror_exception("shim", &session), ConnectionErrorBase);
}

TEST_F(HelpersConnectionErrorVariantsShimTest, TemporaryFailureInNameResolution) {
   g_error_message = "Temporary failure in name resolution";
   netsnmp_session session{};
   EXPECT_THROW(snmp_sess_perror_exception("shim", &session), ConnectionErrorBase);
}

TEST_F(HelpersConnectionErrorVariantsShimTest, CouldNotTranslateHostName) {
   g_error_message = "Could not translate host name";
   netsnmp_session session{};
   EXPECT_THROW(snmp_sess_perror_exception("shim", &session), ConnectionErrorBase);
}

TEST_F(HelpersConnectionErrorVariantsShimTest, NoAddressAssociatedWithHostname) {
   g_error_message = "No address associated with hostname";
   netsnmp_session session{};
   EXPECT_THROW(snmp_sess_perror_exception("shim", &session), ConnectionErrorBase);
}

TEST_F(HelpersConnectionErrorVariantsShimTest, InvalidAddress) {
   g_error_message = "Invalid address";
   netsnmp_session session{};
   EXPECT_THROW(snmp_sess_perror_exception("shim", &session), ConnectionErrorBase);
}

// --- Additional TimeoutErrorBase variant ---

TEST_F(HelpersConnectionErrorVariantsShimTest, TimedOut) {
   g_error_message = "Request timed out";
   netsnmp_session session{};
   EXPECT_THROW(snmp_sess_perror_exception("shim", &session), TimeoutErrorBase);
}
