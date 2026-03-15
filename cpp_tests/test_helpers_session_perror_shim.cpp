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

class HelpersSessionPerrorShimTest : public ::testing::Test {};

TEST_F(HelpersSessionPerrorShimTest, TestConnectionErrorBranch) {
   g_error_message = "Unknown host";
   netsnmp_session session{};
   EXPECT_THROW(snmp_sess_perror_exception("shim", &session), ConnectionErrorBase);
}

TEST_F(HelpersSessionPerrorShimTest, TestTimeoutErrorBranch) {
   g_error_message = "Timeout";
   netsnmp_session session{};
   EXPECT_THROW(snmp_sess_perror_exception("shim", &session), TimeoutErrorBase);
}

TEST_F(HelpersSessionPerrorShimTest, TestPacketErrorBranch) {
   g_error_message = "Cannot send V2 PDU on V1 session";
   netsnmp_session session{};
   EXPECT_THROW(snmp_sess_perror_exception("shim", &session), PacketErrorBase);
}

TEST_F(HelpersSessionPerrorShimTest, TestGenericErrorBranch) {
   g_error_message = "Some other error";
   netsnmp_session session{};
   EXPECT_THROW(snmp_sess_perror_exception("shim", &session), GenericErrorBase);
}
