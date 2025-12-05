#include <gtest/gtest.h>

#include "helpers.h"

class ParseResultsTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(ParseResultsTest, TestBasicResults) {
   std::vector<std::string> inputs = {"SNMPv2-MIB::sysDescr.0 = STRING: Test Description",
                                      "SNMPv2-MIB::sysUpTime.0 = Timeticks: (123) 0:00:01.23",
                                      "SNMPv2-MIB::sysContact.0 = STRING: admin@example.com"};

   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 3);

   // Test first result
   EXPECT_EQ(results[0].oid, "SNMPv2-MIB::sysDescr");
   EXPECT_EQ(results[0].index, "0");
   EXPECT_EQ(results[0].type, "STRING");
   EXPECT_EQ(results[0].value, "Test Description");

   // Test second result
   EXPECT_EQ(results[1].oid, "SNMPv2-MIB::sysUpTime");
   EXPECT_EQ(results[1].index, "0");
   EXPECT_EQ(results[1].type, "Timeticks");
   EXPECT_EQ(results[1].value, "(123) 0:00:01.23");

   // Test third result
   EXPECT_EQ(results[2].oid, "SNMPv2-MIB::sysContact");
   EXPECT_EQ(results[2].index, "0");
   EXPECT_EQ(results[2].type, "STRING");
   EXPECT_EQ(results[2].value, "admin@example.com");
}

TEST_F(ParseResultsTest, TestEmptyInput) {
   std::vector<std::string> inputs;
   auto results = parse_results(inputs);
   EXPECT_TRUE(results.empty());
}

TEST_F(ParseResultsTest, TestNoSuchObjectResults) {
   std::vector<std::string> inputs = {
       "SNMPv2-MIB::sysDescr.1 = No Such Object available on this agent at this OID"};

   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 1);
   EXPECT_EQ(results[0].oid, "SNMPv2-MIB::sysDescr");
   EXPECT_EQ(results[0].index, "1");
   EXPECT_EQ(results[0].type, "NOSUCHOBJECT");
   EXPECT_EQ(results[0].value, "No Such Object available on this agent at this OID");
}

TEST_F(ParseResultsTest, TestNoSuchInstanceResults) {
   std::vector<std::string> inputs = {
       "SNMPv2-MIB::sysDescr.1 = No Such Instance currently exists at this OID"};

   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 1);
   EXPECT_EQ(results[0].oid, "SNMPv2-MIB::sysDescr");
   EXPECT_EQ(results[0].index, "1");
   EXPECT_EQ(results[0].type, "NOSUCHINSTANCE");
   EXPECT_EQ(results[0].value, "No Such Instance currently exists at this OID");
}

TEST_F(ParseResultsTest, TestComplexOIDResults) {
   std::vector<std::string> inputs = {
       "NET-SNMP-AGENT-MIB::nsCacheStatus.1.3.6.1.2.1.4.24.4 = INTEGER: valid(1)",
       ".iso.org.dod.internet.mgmt.mib-2.system.sysContact.0 = STRING: contact@test.com",
       ".1.3.6.1.2.1.1.1.0 = STRING: Test System Description"};

   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 3);

   // Test first result with complex OID
   EXPECT_EQ(results[0].oid, "NET-SNMP-AGENT-MIB::nsCacheStatus.1.3.6.1.2.1.4.24");
   EXPECT_EQ(results[0].index, "4");
   EXPECT_EQ(results[0].type, "INTEGER");
   EXPECT_EQ(results[0].value, "valid(1)");

   // Test second result with full OID path
   EXPECT_EQ(results[1].oid, ".iso.org.dod.internet.mgmt.mib-2.system.sysContact");
   EXPECT_EQ(results[1].index, "0");
   EXPECT_EQ(results[1].type, "STRING");
   EXPECT_EQ(results[1].value, "contact@test.com");

   // Test third result with numeric OID
   EXPECT_EQ(results[2].oid, ".1.3.6.1.2.1.1.1");
   EXPECT_EQ(results[2].index, "0");
   EXPECT_EQ(results[2].type, "STRING");
   EXPECT_EQ(results[2].value, "Test System Description");
}

TEST_F(ParseResultsTest, TestMixedResults) {
   std::vector<std::string> inputs = {
       "SNMPv2-MIB::sysDescr.0 = STRING: Test Description",
       "IF-MIB::ifOperStatus.1 = No Such Instance currently exists at this OID",
       "SNMPv2-MIB::sysServices.0 = INTEGER: 72",
       "IF-MIB::ifType.1 = No Such Object available on this agent at this OID"};

   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 4);

   // Test normal result
   EXPECT_EQ(results[0].oid, "SNMPv2-MIB::sysDescr");
   EXPECT_EQ(results[0].index, "0");
   EXPECT_EQ(results[0].type, "STRING");
   EXPECT_EQ(results[0].value, "Test Description");

   // Test No Such Instance result
   EXPECT_EQ(results[1].oid, "IF-MIB::ifOperStatus");
   EXPECT_EQ(results[1].index, "1");
   EXPECT_EQ(results[1].type, "NOSUCHINSTANCE");
   EXPECT_EQ(results[1].value, "No Such Instance currently exists at this OID");

   // Test INTEGER result
   EXPECT_EQ(results[2].oid, "SNMPv2-MIB::sysServices");
   EXPECT_EQ(results[2].index, "0");
   EXPECT_EQ(results[2].type, "INTEGER");
   EXPECT_EQ(results[2].value, "72");

   // Test No Such Object result
   EXPECT_EQ(results[3].oid, "IF-MIB::ifType");
   EXPECT_EQ(results[3].index, "1");
   EXPECT_EQ(results[3].type, "NOSUCHOBJECT");
   EXPECT_EQ(results[3].value, "No Such Object available on this agent at this OID");
}

TEST_F(ParseResultsTest, TestLongValues) {
   std::vector<std::string> inputs = {
       "SNMPv2-MIB::sysDescr.0 = STRING: " + std::string(1024, 'A'),    // Long string value
       "SNMPv2-MIB::sysLocation.0 = STRING: " + std::string(2048, 'B'), // Very long string
       "SNMPv2-MIB::sysName.0 = STRING: " + std::string(4096, 'C')      // Even longer string
   };

   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 3);

   // Test first result
   EXPECT_EQ(results[0].oid, "SNMPv2-MIB::sysDescr");
   EXPECT_EQ(results[0].index, "0");
   EXPECT_EQ(results[0].type, "STRING");
   EXPECT_EQ(results[0].value, std::string(1024, 'A'));

   // Test second result
   EXPECT_EQ(results[1].oid, "SNMPv2-MIB::sysLocation");
   EXPECT_EQ(results[1].index, "0");
   EXPECT_EQ(results[1].type, "STRING");
   EXPECT_EQ(results[1].value, std::string(2048, 'B'));

   // Test third result
   EXPECT_EQ(results[2].oid, "SNMPv2-MIB::sysName");
   EXPECT_EQ(results[2].index, "0");
   EXPECT_EQ(results[2].type, "STRING");
   EXPECT_EQ(results[2].value, std::string(4096, 'C'));
}

TEST_F(ParseResultsTest, TestWhitespaceTrailing) {
   std::vector<std::string> inputs = {"SNMPv2-MIB::sysDescr.0 = STRING: Test Description     ",
                                      "SNMPv2-MIB::sysContact.0 = STRING: contact@test.com       ",
                                      "SNMPv2-MIB::sysLocation.0 = STRING: Some Location    ",
                                      "SNMPv2-MIB::sysServices.0 = INTEGER: 72      "};

   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 4);

   // Test whitespace trimming in first result
   EXPECT_EQ(results[0].oid, "SNMPv2-MIB::sysDescr");
   EXPECT_EQ(results[0].index, "0");
   EXPECT_EQ(results[0].type, "STRING");
   EXPECT_EQ(results[0].value, "Test Description");

   // Test tab trimming in second result
   EXPECT_EQ(results[1].oid, "SNMPv2-MIB::sysContact");
   EXPECT_EQ(results[1].index, "0");
   EXPECT_EQ(results[1].type, "STRING");
   EXPECT_EQ(results[1].value, "contact@test.com");

   // Test newline trimming in third result
   EXPECT_EQ(results[2].oid, "SNMPv2-MIB::sysLocation");
   EXPECT_EQ(results[2].index, "0");
   EXPECT_EQ(results[2].type, "STRING");
   EXPECT_EQ(results[2].value, "Some Location");

   // Test whitespace trimming with integer value
   EXPECT_EQ(results[3].oid, "SNMPv2-MIB::sysServices");
   EXPECT_EQ(results[3].index, "0");
   EXPECT_EQ(results[3].type, "INTEGER");
   EXPECT_EQ(results[3].value, "72");
}

TEST_F(ParseResultsTest, TestJustTimeticks) {
   std::vector<std::string> inputs = {
       "DISMAN-EXPRESSION-MIB::sysUpTimeInstance = Timeticks: (8910208) 1 day, 0:45:02.08",
       "DISMAN-EXPRESSION-MIB::sysUpTimeInstance = 8912330"};

   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 2);

   // Test first result
   EXPECT_EQ(results[0].oid, "DISMAN-EXPRESSION-MIB::sysUpTimeInstance");
   EXPECT_EQ(results[0].index, "");
   EXPECT_EQ(results[0].type, "Timeticks");
   EXPECT_EQ(results[0].value, "(8910208) 1 day, 0:45:02.08");

   // Test second result
   EXPECT_EQ(results[1].oid, "DISMAN-EXPRESSION-MIB::sysUpTimeInstance");
   EXPECT_EQ(results[1].index, "");
   EXPECT_EQ(results[1].type, "Timeticks");
   EXPECT_EQ(results[1].value, "8912330");
}

TEST_F(ParseResultsTest, TestSnmpwalkStringType) {
   std::vector<std::string> inputs = {
       "SNMPv2-MIB::sysDescr.0 = STRING: Linux carlkidcrypto-w 5.15.167.4-microsoft-standard-WSL2 "
       "#1 SMP Tue Nov 5 00:21:55 UTC 2024 x86_64"};
   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 1);
   EXPECT_EQ(results[0].oid, "SNMPv2-MIB::sysDescr");
   EXPECT_EQ(results[0].index, "0");
   EXPECT_EQ(results[0].type, "STRING");
   EXPECT_EQ(results[0].value,
             "Linux carlkidcrypto-w 5.15.167.4-microsoft-standard-WSL2 #1 SMP Tue Nov 5 00:21:55 "
             "UTC 2024 x86_64");
}

TEST_F(ParseResultsTest, TestSnmpwalkOidType) {
   std::vector<std::string> inputs = {"SNMPv2-MIB::sysObjectID.0 = OID: NET-SNMP-TC::linux"};
   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 1);
   EXPECT_EQ(results[0].oid, "SNMPv2-MIB::sysObjectID");
   EXPECT_EQ(results[0].index, "0");
   EXPECT_EQ(results[0].type, "OID");
   EXPECT_EQ(results[0].value, "NET-SNMP-TC::linux");
}

TEST_F(ParseResultsTest, TestSnmpwalkIntegerTypes) {
   std::vector<std::string> inputs = {"IF-MIB::ifNumber.0 = INTEGER: 4",
                                      "IF-MIB::ifType.1 = INTEGER: softwareLoopback(24)",
                                      "RFC1213-MIB::tcpMaxConn.0 = INTEGER: -1"};
   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 3);

   EXPECT_EQ(results[0].oid, "IF-MIB::ifNumber");
   EXPECT_EQ(results[0].index, "0");
   EXPECT_EQ(results[0].type, "INTEGER");
   EXPECT_EQ(results[0].value, "4");

   EXPECT_EQ(results[1].oid, "IF-MIB::ifType");
   EXPECT_EQ(results[1].index, "1");
   EXPECT_EQ(results[1].type, "INTEGER");
   EXPECT_EQ(results[1].value, "softwareLoopback(24)");

   EXPECT_EQ(results[2].oid, "RFC1213-MIB::tcpMaxConn");
   EXPECT_EQ(results[2].index, "0");
   EXPECT_EQ(results[2].type, "INTEGER");
   EXPECT_EQ(results[2].value, "-1");
}

TEST_F(ParseResultsTest, TestSnmpwalkGaugeCounterTypes) {
   std::vector<std::string> inputs = {"IF-MIB::ifSpeed.1 = Gauge32: 10000000",
                                      "IF-MIB::ifOutOctets.1 = Counter32: 1738754",
                                      "IP-MIB::ipSystemStatsHCInReceives.ipv4 = Counter64: 22711"};
   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 3);

   EXPECT_EQ(results[0].oid, "IF-MIB::ifSpeed");
   EXPECT_EQ(results[0].index, "1");
   EXPECT_EQ(results[0].type, "Gauge32");
   EXPECT_EQ(results[0].value, "10000000");

   EXPECT_EQ(results[1].oid, "IF-MIB::ifOutOctets");
   EXPECT_EQ(results[1].index, "1");
   EXPECT_EQ(results[1].type, "Counter32");
   EXPECT_EQ(results[1].value, "1738754");

   EXPECT_EQ(results[2].oid, "IP-MIB::ipSystemStatsHCInReceives");
   EXPECT_EQ(results[2].index, "ipv4");
   EXPECT_EQ(results[2].type, "Counter64");
   EXPECT_EQ(results[2].value, "22711");
}

TEST_F(ParseResultsTest, TestSnmpwalkComplexStringTypes) {
   std::vector<std::string> inputs = {
       "HOST-RESOURCES-MIB::hrSystemDate.0 = STRING: 2025-7-9,7:36:11.0,-7:0",
       "IF-MIB::ifPhysAddress.1 = STRING:"};
   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 2);

   EXPECT_EQ(results[0].oid, "HOST-RESOURCES-MIB::hrSystemDate");
   EXPECT_EQ(results[0].index, "0");
   EXPECT_EQ(results[0].type, "STRING");
   EXPECT_EQ(results[0].value, "2025-7-9,7:36:11.0,-7:0");

   EXPECT_EQ(results[1].oid, "IF-MIB::ifPhysAddress");
   EXPECT_EQ(results[1].index, "1");
   EXPECT_EQ(results[1].type, "STRING");
   EXPECT_EQ(results[1].value, "");
}

TEST_F(ParseResultsTest, TestSnmpwalkHexStringType) {
   std::vector<std::string> inputs = {
       "RFC1213-MIB::atPhysAddress.2.1.172.25.0.1 = Hex-STRING: 00 15 5D 6E 34 05"};
   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 1);

   EXPECT_EQ(results[0].oid, "RFC1213-MIB::atPhysAddress");
   EXPECT_EQ(results[0].index, "2.1.172.25.0.1");
   EXPECT_EQ(results[0].type, "Hex-STRING");
   EXPECT_EQ(results[0].value, "00 15 5D 6E 34 05");
}

TEST_F(ParseResultsTest, TestSnmpwalkIpAddressType) {
   std::vector<std::string> inputs = {
       "RFC1213-MIB::ipAdEntAddr.172.25.10.171 = IpAddress: 172.25.10.171"};
   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 1);

   EXPECT_EQ(results[0].oid, "RFC1213-MIB::ipAdEntAddr");
   EXPECT_EQ(results[0].index, "172.25.10.171");
   EXPECT_EQ(results[0].type, "IpAddress");
   EXPECT_EQ(results[0].value, "172.25.10.171");
}

TEST_F(ParseResultsTest, TestSnmpwalkNetworkAddressType) {
   std::vector<std::string> inputs = {
       "RFC1213-MIB::atNetAddress.2.1.172.25.0.1 = Network Address: AC:19:00:01"};
   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 1);

   EXPECT_EQ(results[0].oid, "RFC1213-MIB::atNetAddress");
   EXPECT_EQ(results[0].index, "2.1.172.25.0.1");
   EXPECT_EQ(results[0].type, "Network Address");
   EXPECT_EQ(results[0].value, "AC:19:00:01");
}

TEST_F(ParseResultsTest, TestStringValuesWithQuotes) {
   // Test for issue #355: String values returned with extra quotes
   std::vector<std::string> inputs = {"SNMPv2-MIB::sysDescr.0 = STRING: \"LEDI Network TS\"",
                                      "SNMPv2-MIB::sysName.0 = STRING: \"TOP\"",
                                      "SNMPv2-MIB::sysContact.0 = STRING: \"admin@example.com\"",
                                      "IF-MIB::ifDescr.1 = STRING: \"GigabitEthernet0/0/1\""};

   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 4);

   // Test that quotes are stripped from STRING values
   EXPECT_EQ(results[0].oid, "SNMPv2-MIB::sysDescr");
   EXPECT_EQ(results[0].index, "0");
   EXPECT_EQ(results[0].type, "STRING");
   EXPECT_EQ(results[0].value, "LEDI Network TS");

   EXPECT_EQ(results[1].oid, "SNMPv2-MIB::sysName");
   EXPECT_EQ(results[1].index, "0");
   EXPECT_EQ(results[1].type, "STRING");
   EXPECT_EQ(results[1].value, "TOP");

   EXPECT_EQ(results[2].oid, "SNMPv2-MIB::sysContact");
   EXPECT_EQ(results[2].index, "0");
   EXPECT_EQ(results[2].type, "STRING");
   EXPECT_EQ(results[2].value, "admin@example.com");

   EXPECT_EQ(results[3].oid, "IF-MIB::ifDescr");
   EXPECT_EQ(results[3].index, "1");
   EXPECT_EQ(results[3].type, "STRING");
   EXPECT_EQ(results[3].value, "GigabitEthernet0/0/1");
}

TEST_F(ParseResultsTest, TestStringValuesWithoutQuotes) {
   // Test that strings without quotes still work correctly
   std::vector<std::string> inputs = {"SNMPv2-MIB::sysDescr.0 = STRING: LEDI Network TS",
                                      "SNMPv2-MIB::sysName.0 = STRING: TOP",
                                      "SNMPv2-MIB::sysContact.0 = STRING: admin@example.com"};

   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 3);

   // Test that values remain unchanged
   EXPECT_EQ(results[0].oid, "SNMPv2-MIB::sysDescr");
   EXPECT_EQ(results[0].index, "0");
   EXPECT_EQ(results[0].type, "STRING");
   EXPECT_EQ(results[0].value, "LEDI Network TS");

   EXPECT_EQ(results[1].oid, "SNMPv2-MIB::sysName");
   EXPECT_EQ(results[1].index, "0");
   EXPECT_EQ(results[1].type, "STRING");
   EXPECT_EQ(results[1].value, "TOP");

   EXPECT_EQ(results[2].oid, "SNMPv2-MIB::sysContact");
   EXPECT_EQ(results[2].index, "0");
   EXPECT_EQ(results[2].type, "STRING");
   EXPECT_EQ(results[2].value, "admin@example.com");
}

TEST_F(ParseResultsTest, TestNonStringValuesWithQuotesNotStripped) {
   // Test that quotes are stripped consistently from all types including STRING, INTEGER, and OID
   std::vector<std::string> inputs = {
       "SNMP-TARGET-MIB::snmpTargetAddrTAddress.test = STRING: \"1234\"",
       "IF-MIB::ifOperStatus.1 = INTEGER: \"up(1)\"", // hypothetical case
       "SNMPv2-MIB::sysObjectID.0 = OID: \"NET-SNMP-TC::linux\""};

   auto results = parse_results(inputs);
   ASSERT_EQ(results.size(), 3);

   // STRING type should have quotes stripped
   EXPECT_EQ(results[0].type, "STRING");
   EXPECT_EQ(results[0].value, "1234");

   // INTEGER type should have quotes stripped as well for consistency
   EXPECT_EQ(results[1].type, "INTEGER");
   EXPECT_EQ(results[1].value, "up(1)");

   // OID type should have quotes stripped
   EXPECT_EQ(results[2].type, "OID");
   EXPECT_EQ(results[2].value, "NET-SNMP-TC::linux");
}
