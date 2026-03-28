#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "snmpbulkget.h"

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;
   *response = NULL;
   return STAT_ERROR;
}

class SnmpBulkGetStatErrorShimTest : public ::testing::Test {};

TEST_F(SnmpBulkGetStatErrorShimTest, TestStatErrorPathThrows) {
   std::vector<std::string> args = {"-v", "2c", "-c", "public", "localhost:11161", "1.3.6.1.2.1.1"};
   EXPECT_ANY_THROW({ auto results = snmpbulkget(args, "testing_bulkget_stat_error_shim"); });
}
