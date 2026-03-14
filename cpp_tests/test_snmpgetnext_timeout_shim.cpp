/* Shim that returns STAT_TIMEOUT so the timeout error branch in snmpgetnext() is covered. */
#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmpgetnext.h"

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;
   *response = NULL;
   return STAT_TIMEOUT;
}

class SnmpGetNextTimeoutShimTest : public ::testing::Test {};

TEST_F(SnmpGetNextTimeoutShimTest, TestTimeoutThrowsTimeoutError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysLocation.0"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpgetnext(args, "testing_getnext_timeout_shim");
          } catch (TimeoutErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("Timeout") != std::string::npos ||
                         msg.find("No Response from") != std::string::npos);
             throw;
          }
       },
       TimeoutErrorBase);
}
