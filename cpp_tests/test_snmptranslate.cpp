#include <gtest/gtest.h>

#include "exceptionsbase.h"
#include "snmptranslate.h"

class SnmpTranslateTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SnmpTranslateTest, TestTranslateToNumeric) {
   std::vector<std::string> args = {"-On", "SNMPv2-MIB::sysDescr.0"};
   auto result = snmptranslate(args, "testing_snmptranslate_numeric");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_EQ(result[0], ".1.3.6.1.2.1.1.1.0");
}

TEST_F(SnmpTranslateTest, TestTranslateFromNumeric) {
   std::vector<std::string> args = {".1.3.6.1.2.1.1.1.0"};
   auto result = snmptranslate(args, "testing_snmptranslate_symbolic");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_NE(result[0].find("sysDescr.0"), std::string::npos);
}

TEST_F(SnmpTranslateTest, TestTranslateFullOid) {
   std::vector<std::string> args = {"-Of", ".1.3.6.1.2.1.1.1.0"};
   auto result = snmptranslate(args, "testing_snmptranslate_full");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_EQ(result[0], ".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0");
}

TEST_F(SnmpTranslateTest, TestTranslateShortOid) {
   std::vector<std::string> args = {"-Os", ".1.3.6.1.2.1.1.1.0"};
   auto result = snmptranslate(args, "testing_snmptranslate_short");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_EQ(result[0], "sysDescr.0");
}

TEST_F(SnmpTranslateTest, TestTranslateMultipleOids) {
   std::vector<std::string> args = {"-On", "SNMPv2-MIB::sysDescr.0", "SNMPv2-MIB::sysUpTime.0"};
   auto result = snmptranslate(args, "testing_snmptranslate_multi");
   ASSERT_EQ(result.size(), 2u);
   EXPECT_EQ(result[0], ".1.3.6.1.2.1.1.1.0");
   EXPECT_EQ(result[1], ".1.3.6.1.2.1.1.3.0");
}

TEST_F(SnmpTranslateTest, TestRandomAccess) {
   std::vector<std::string> args = {"-IR", "-On", "sysDescr.0"};
   auto result = snmptranslate(args, "testing_snmptranslate_ir");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_EQ(result[0], ".1.3.6.1.2.1.1.1.0");
}

TEST_F(SnmpTranslateTest, TestFindAllRegex) {
   std::vector<std::string> args = {"-TB", "sysDescr"};
   auto result = snmptranslate(args, "testing_snmptranslate_tb");
   ASSERT_GE(result.size(), 1u);
   EXPECT_NE(result[0].find("sysDescr"), std::string::npos);
}

TEST_F(SnmpTranslateTest, TestPrintDescription) {
   std::vector<std::string> args = {"-Td", "SNMPv2-MIB::sysDescr.0"};
   auto result = snmptranslate(args, "testing_snmptranslate_td");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_NE(result[0].find("sysDescr"), std::string::npos);
}

TEST_F(SnmpTranslateTest, TestPrintTree) {
   std::vector<std::string> args = {"-Tp", "SNMPv2-MIB::system"};
   auto result = snmptranslate(args, "testing_snmptranslate_tp");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_NE(result[0].find("system"), std::string::npos);
}

TEST_F(SnmpTranslateTest, TestVersionFlag) {
   std::vector<std::string> args = {"-V"};
   auto result = snmptranslate(args, "testing_snmptranslate_version");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_NE(result[0].find("NET-SNMP version:"), std::string::npos);
}

TEST_F(SnmpTranslateTest, TestHelpThrowsParseError) {
   std::vector<std::string> args = {"-h"};
   EXPECT_THROW(snmptranslate(args, "testing_snmptranslate_help"), ParseErrorBase);
}

TEST_F(SnmpTranslateTest, TestInvalidOptionThrowsParseError) {
   std::vector<std::string> args = {"-Z", "SNMPv2-MIB::sysDescr.0"};
   EXPECT_THROW(snmptranslate(args, "testing_snmptranslate_invalid_opt"), ParseErrorBase);
}

TEST_F(SnmpTranslateTest, TestInvalidTOptionThrowsParseError) {
   std::vector<std::string> args = {"-TX", "SNMPv2-MIB::sysDescr.0"};
   EXPECT_THROW(snmptranslate(args, "testing_snmptranslate_invalid_t"), ParseErrorBase);
}

TEST_F(SnmpTranslateTest, TestInvalidWidthThrowsParseError) {
   std::vector<std::string> args = {"-w", "0", "SNMPv2-MIB::sysDescr.0"};
   EXPECT_THROW(snmptranslate(args, "testing_snmptranslate_invalid_w"), ParseErrorBase);
}

TEST_F(SnmpTranslateTest, TestMissingOidThrowsParseError) {
   std::vector<std::string> args = {};
   EXPECT_THROW(snmptranslate(args, "testing_snmptranslate_missing_oid"), ParseErrorBase);
}

TEST_F(SnmpTranslateTest, TestStdinDashThrowsParseError) {
   std::vector<std::string> args = {"-"};
   EXPECT_THROW(snmptranslate(args, "testing_snmptranslate_stdin"), ParseErrorBase);
}

TEST_F(SnmpTranslateTest, TestUnknownOidThrows) {
   std::vector<std::string> args = {"NONEXISTENT-MIB::doesNotExist.0"};
   EXPECT_THROW(snmptranslate(args, "testing_snmptranslate_unknown_oid"), GenericErrorBase);
}

TEST_F(SnmpTranslateTest, TestUnknownRandomAccessOidThrows) {
   std::vector<std::string> args = {"-IR", "nonexistentObjectIdentifierXYZ"};
   EXPECT_THROW(snmptranslate(args, "testing_snmptranslate_unknown_ir"), UnknownObjectIDErrorBase);
}
