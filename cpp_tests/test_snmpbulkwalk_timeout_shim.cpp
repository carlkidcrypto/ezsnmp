/* Shim that returns STAT_TIMEOUT so the timeout error branch in snmpbulkwalk() is covered. */
#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "datatypes.h"
#include "exceptionsbase.h"
#include "snmpbulkwalk.h"

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu,
                                   netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;
   *response = NULL;
   return STAT_TIMEOUT;
}

class SnmpBulkWalkTimeoutShimTest : public ::testing::Test {};

TEST_F(SnmpBulkWalkTimeoutShimTest, TestTimeoutThrowsTimeoutError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_THROW(
       {
          try {
             auto results = snmpbulkwalk(args, "testing_bulkwalk_timeout_shim");
          } catch (TimeoutErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("Timeout") != std::string::npos ||
                         msg.find("No Response from") != std::string::npos);
             throw;
          }
       },
       TimeoutErrorBase);
}
