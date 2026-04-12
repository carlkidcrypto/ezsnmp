/* NOSUCHNAME shim for snmpbulkget: covers the SNMP_ERR_NOSUCHNAME branch in
 * snmpbulkget.cpp (the `if (response->errstat == SNMP_ERR_NOSUCHNAME)` path).
 *
 * When the response has errstat == SNMP_ERR_NOSUCHNAME, snmpbulkget silently
 * terminates (no exception raised) and returns an empty result vector.  This
 * mirrors the analogous test for snmpwalk and snmpbulkwalk.
 */
#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmpbulkget.h"

extern "C" int snmp_synch_response(netsnmp_session *ss, netsnmp_pdu *pdu, netsnmp_pdu **response) {
   (void)ss;
   (void)pdu;

   netsnmp_pdu *fake_response = snmp_pdu_create(SNMP_MSG_RESPONSE);
   fake_response->errstat = SNMP_ERR_NOSUCHNAME;
   fake_response->errindex = 0;

   *response = fake_response;
   return STAT_SUCCESS;
}

class SnmpBulkGetNoSuchNameShimTest : public ::testing::Test {};

/* Base case: NOSUCHNAME response causes snmpbulkget to return an empty result
 * vector without raising any exception. */
TEST_F(SnmpBulkGetNoSuchNameShimTest, TestNoSuchNameReturnsEmptyWithoutThrowing) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORDescr"};

   EXPECT_NO_THROW({
      auto results = snmpbulkget(args, "testing_bulkget_nosuchname");
      EXPECT_TRUE(results.empty());
   });
}

/* Verify the same behaviour when multiple OIDs are requested. */
TEST_F(SnmpBulkGetNoSuchNameShimTest, TestNoSuchNameWithMultipleOidsReturnsEmpty) {
   std::vector<std::string> args = {"-v",
                                    "2c",
                                    "-c",
                                    "public",
                                    "localhost:11161",
                                    "SNMPv2-MIB::sysDescr.0",
                                    "SNMPv2-MIB::sysORDescr"};

   EXPECT_NO_THROW({
      auto results = snmpbulkget(args, "testing_bulkget_nosuchname_multi");
      EXPECT_TRUE(results.empty());
   });
}
