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
   std::vector<std::string> inputs = {"SNMPv2-MIB::sysDescr.0 = STRING: Test Description    ",
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