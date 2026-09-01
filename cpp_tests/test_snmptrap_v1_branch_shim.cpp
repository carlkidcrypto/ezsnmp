/* Shim tests for the SNMPv1 code path inside snmptrap().
 *
 * The entire #ifndef NETSNMP_DISABLE_SNMPV1 block in snmptrap.cpp is normally
 * unreachable from the existing test suite because all tests use -v 2c.  This
 * file drives the V1 branch by:
 *
 *   1. Passing "-v" "1" so snmp_parse_args sets session.version = SNMP_VERSION_1.
 *   2. Shimming snmp_add to return a fake non-NULL session pointer, snmp_close
 *      to accept it, and snmp_send to simulate success or failure.
 *
 * Branches covered:
 *   - session.version == SNMP_VERSION_1 (true branch).
 *   - inform && SNMP_VERSION_1: "Cannot send INFORM as SNMPv1 PDU" early exit.
 *   - argv[arg][0] == 0: use default enterprise OID path.
 *   - Full V1 PDU construction and send path (success).
 *   - snmp_send failure in V1 context (snmp_sess_perror_exception called).
 */

#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <cstring>

#include "exceptionsbase.h"
#include "snmptrap.h"

namespace {

bool g_snmp_send_fail = false;
// Reuse a stack-allocated dummy as the fake session pointer.
netsnmp_session g_fake_session{};

} // namespace

// Override snmp_add to return a fake session so the V1 branch can proceed past
// the "ss == NULL" guard without attempting a real network connection.
extern "C" netsnmp_session *snmp_add(
    netsnmp_session *in_session,
    netsnmp_transport *transport,
    int (*fpre_parse)(netsnmp_session *, netsnmp_transport *, void *, int),
    int (*fpost_parse)(netsnmp_session *, netsnmp_pdu *, int)) {
   (void)in_session;
   (void)transport;
   (void)fpre_parse;
   (void)fpost_parse;
   return &g_fake_session;
}

// Override snmp_send: return 1 (success) or 0 (failure) based on the flag.
extern "C" int snmp_send(netsnmp_session *session, netsnmp_pdu *pdu) {
   (void)session;
   (void)pdu;
   return g_snmp_send_fail ? 0 : 1;
}

// Override snmp_error so snmp_sess_perror_exception does not dereference the
// fake session struct when snmp_send fails.
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
      *p_str = strdup("v1 send failed");
   }
}

// Override snmp_close so the RAII / post-send cleanup does not crash on the
// fake session pointer.
extern "C" int snmp_close(netsnmp_session *session) {
   (void)session;
   return 0;
}

class SnmpTrapV1BranchShimTest : public ::testing::Test {
  protected:
   void SetUp() override {
      g_snmp_send_fail = false;
      g_fake_session = netsnmp_session{};
   }
   void TearDown() override { g_snmp_send_fail = false; }
};

/* -----------------------------------------------------------------------
 * Test 1: V1 with default enterprise OID (argv[arg][0] == 0)
 *
 * Args layout for SNMPv1 trap:
 *   -v 1 -c public <host> <enterprise> <agent> <generic-trap> <specific-trap> <uptime>
 *
 * Passing "" as enterprise exercises the argv[arg][0] == 0 branch that copies
 * objid_enterprise into the PDU instead of parsing an OID string.
 * Passing "" as uptime exercises the (description == NULL || *description == 0)
 * branch that calls get_uptime().
 * ----------------------------------------------------------------------- */
TEST_F(SnmpTrapV1BranchShimTest, V1TrapWithDefaultEnterpriseAndGetUptimeBranch) {
   std::vector<std::string> args = {
       "-v",      "1",
       "-c",      "public",
       "localhost:11162",
       "",           // enterprise: "" -> argv[arg][0]==0 -> use objid_enterprise
       "127.0.0.1",  // agent address
       "6",          // generic-trap
       "0",          // specific-trap
       "",           // uptime: "" -> description==NULL or *desc==0 -> get_uptime()
   };

   // With a successful snmp_send the function should return 0.
   int rc = snmptrap(args, "testing_snmptrap_v1_default_enterprise");
   EXPECT_EQ(rc, 0);
}

/* -----------------------------------------------------------------------
 * Test 2: V1 inform rejected ("Cannot send INFORM as SNMPv1 PDU")
 *
 * Passing -Ci activates inform=1 inside snmptrap_optProc.  When combined
 * with -v 1 the function hits the early-exit guard on line ~255:
 *   if (inform) { fprintf(stderr, "Cannot send INFORM …"); goto out; }
 * The function returns exitval=1 without throwing.
 * ----------------------------------------------------------------------- */
TEST_F(SnmpTrapV1BranchShimTest, V1InformEarlyExitReturnsNonZero) {
   std::vector<std::string> args = {
       "-v",  "1",
       "-c",  "public",
       "-Ci",             // sets inform=1
       "localhost:11162",
       "",    "127.0.0.1", "6", "0", "",
   };

   // No exception: the function exits early via goto out and returns 1.
   int rc = snmptrap(args, "testing_snmptrap_v1_inform_rejected");
   EXPECT_NE(rc, 0);
}

/* -----------------------------------------------------------------------
 * Test 3: V1 with an explicit uptime value (non-empty description)
 *
 * Passing a non-empty uptime string exercises the else branch:
 *   pdu->time = atol(description);
 * ----------------------------------------------------------------------- */
TEST_F(SnmpTrapV1BranchShimTest, V1TrapWithExplicitUptimeBranch) {
   std::vector<std::string> args = {
       "-v",      "1",
       "-c",      "public",
       "localhost:11162",
       "",           // enterprise: default
       "127.0.0.1",  // agent address
       "6",          // generic-trap
       "0",          // specific-trap
       "12345",      // explicit uptime -> atol() branch
   };

   int rc = snmptrap(args, "testing_snmptrap_v1_explicit_uptime");
   EXPECT_EQ(rc, 0);
}

/* -----------------------------------------------------------------------
 * Test 4: V1 snmp_send failure triggers exception path
 *
 * When snmp_send returns 0 the code calls snmp_sess_perror_exception which
 * throws GenericErrorBase (or a subclass).
 * ----------------------------------------------------------------------- */
TEST_F(SnmpTrapV1BranchShimTest, V1SendFailureThrowsException) {
   g_snmp_send_fail = true;

   std::vector<std::string> args = {
       "-v",      "1",
       "-c",      "public",
       "localhost:11162",
       "",
       "127.0.0.1",
       "6",
       "0",
       "",
   };

   EXPECT_THROW({ snmptrap(args, "testing_snmptrap_v1_send_fail"); }, GenericErrorBase);
}
