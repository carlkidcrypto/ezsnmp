#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <cstring>

#include "exceptionsbase.h"
#include "snmptrap.h"

namespace {

bool g_return_fake_session = false;
netsnmp_session g_fake_session{};

} // namespace

// Override snmp_add to return NULL or a fake session depending on the test.
extern "C" netsnmp_session *snmp_add(
    netsnmp_session *in_session,
    netsnmp_transport *transport,
    int (*fpre_parse)(netsnmp_session *, netsnmp_transport *, void *, int),
    int (*fpost_parse)(netsnmp_session *, netsnmp_pdu *, int)) {
   (void)in_session;
   (void)transport;
   (void)fpre_parse;
   (void)fpost_parse;
   return g_return_fake_session ? &g_fake_session : nullptr;
}

// Override snmp_pdu_create to return nullptr, simulating PDU allocation failure.
extern "C" netsnmp_pdu *snmp_pdu_create(int type) {
   (void)type;
   return nullptr;
}

// Override snmp_error so snmp_sess_perror_exception does not dereference the
// uninitialised/partial session struct that snmptrap passes when ss is NULL.
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
      *p_str = strdup("snmp_add returned NULL");
   }
}

// Override snmp_close so snmp_sess_perror_exception does not try to close the
// partial session struct.
extern "C" int snmp_close(netsnmp_session *session) {
   (void)session;
   return 0;
}

class SnmpTrapNullShimTest : public ::testing::Test {
  protected:
   void SetUp() override {
      g_return_fake_session = false;
      g_fake_session = netsnmp_session{};
   }
   void TearDown() override { g_return_fake_session = false; }
};

TEST_F(SnmpTrapNullShimTest, TestNullSessionThrowsException) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11162", "", ".1.3.6.1.6.3.1.1.5.1"};
   EXPECT_ANY_THROW({ snmptrap(args, "testing_snmptrap_null_shim"); });
}

TEST_F(SnmpTrapNullShimTest, TestV1NullPduThrowsGenericError) {
   g_return_fake_session = true;
   std::vector<std::string> args = {"-v", "1",         "-c", "public", "localhost:11162",
                                    "",   "127.0.0.1", "6",  "0",      ""};
   EXPECT_THROW({ snmptrap(args, "testing_snmptrap_v1_null_pdu"); }, GenericErrorBase);
}

TEST_F(SnmpTrapNullShimTest, TestV2cNullPduThrowsGenericError) {
   g_return_fake_session = true;
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11162", "", ".1.3.6.1.6.3.1.1.5.1"};
   EXPECT_THROW({ snmptrap(args, "testing_snmptrap_v2c_null_pdu"); }, GenericErrorBase);
}
