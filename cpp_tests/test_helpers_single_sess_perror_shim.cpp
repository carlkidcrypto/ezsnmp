/* Shim-test for snmp_single_sess_perror_exception().
 *
 * snmp_single_sess_perror_exception() uses the single-session API
 * (snmp_sess_error / void* opaque handle) instead of the global-session API
 * (snmp_error / netsnmp_session*).  We stub out snmp_sess_error() to inject
 * controlled error messages and verify that the function maps each message to
 * the expected exception type – mirroring the approach used by
 * test_helpers_session_perror_shim.cpp for snmp_sess_perror_exception().
 */

#include <gtest/gtest.h>

#include <cstring>

#include "exceptionsbase.h"
#include "helpers.h"

static std::string g_error_message = "generic error";

/* Stub for the single-session error accessor used by
 * snmp_single_sess_perror_exception(). */
extern "C" void snmp_sess_error(void *sessp, int *p_errno, int *p_snmp_errno, char **p_str) {
   (void)sessp;
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

class HelpersSingleSessPerrorShimTest : public ::testing::Test {};

TEST_F(HelpersSingleSessPerrorShimTest, TestConnectionErrorBranch) {
   g_error_message = "Unknown host";
   EXPECT_THROW(snmp_single_sess_perror_exception("shim", nullptr), ConnectionErrorBase);
}

TEST_F(HelpersSingleSessPerrorShimTest, TestTimeoutErrorBranch) {
   g_error_message = "Timeout";
   EXPECT_THROW(snmp_single_sess_perror_exception("shim", nullptr), TimeoutErrorBase);
}

TEST_F(HelpersSingleSessPerrorShimTest, TestPacketErrorBranch) {
   g_error_message = "Cannot send V2 PDU on V1 session";
   EXPECT_THROW(snmp_single_sess_perror_exception("shim", nullptr), PacketErrorBase);
}

TEST_F(HelpersSingleSessPerrorShimTest, TestGenericErrorBranch) {
   g_error_message = "Some other error";
   EXPECT_THROW(snmp_single_sess_perror_exception("shim", nullptr), GenericErrorBase);
}
