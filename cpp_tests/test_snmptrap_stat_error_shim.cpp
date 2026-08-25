#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmptrap.h"

// Override snmp_send to return 0 (failure), triggering the send-error path in
// snmptrap() where snmp_sess_perror_exception is called with the active session.
extern "C" int snmp_send(netsnmp_session *session, netsnmp_pdu *pdu) {
   (void)session;
   (void)pdu;
   return 0;
}

class SnmpTrapStatErrorShimTest : public ::testing::Test {};

TEST_F(SnmpTrapStatErrorShimTest, TestSendFailureThrowsException) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11162", "", ".1.3.6.1.6.3.1.1.5.1"};
   EXPECT_ANY_THROW({ snmptrap(args, "testing_snmptrap_stat_error_shim"); });
}
