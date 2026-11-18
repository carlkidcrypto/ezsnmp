#include <gtest/gtest.h>
// clang-format off
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/mib_api.h>
#include <net-snmp/library/snmp_debug.h>
// clang-format on

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

TEST_F(SnmpTranslateTest, TestFindAllRegexWithDescription) {
   std::vector<std::string> args = {"-TB", "-Td", "sysDescr"};
   auto result = snmptranslate(args, "testing_snmptranslate_tb_td");
   ASSERT_GE(result.size(), 1u);
   EXPECT_NE(result[0].find("sysDescr"), std::string::npos);
}

TEST_F(SnmpTranslateTest, TestFindAllRegexNotFoundThrows) {
   std::vector<std::string> args = {"-TB", "nonexistentObjectIdentifierXYZ"};
   EXPECT_THROW(snmptranslate(args, "testing_snmptranslate_tb_not_found"),
                UnknownObjectIDErrorBase);
}

TEST_F(SnmpTranslateTest, TestRegexAccess) {
   std::vector<std::string> args = {"-Ib", "-On", "sysDescr"};
   auto result = snmptranslate(args, "testing_snmptranslate_ib");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_NE(result[0].find(".1.3.6.1.2.1.1.1"), std::string::npos);
}

TEST_F(SnmpTranslateTest, TestRegexAccessNotFoundThrows) {
   std::vector<std::string> args = {"-Ib", "nonexistentRegexObjectXYZ"};
   EXPECT_THROW(snmptranslate(args, "testing_snmptranslate_ib_not_found"),
                UnknownObjectIDErrorBase);
}

TEST_F(SnmpTranslateTest, TestLoadMibs) {
   std::vector<std::string> args_all = {"-m", "ALL", "-On", "SNMPv2-MIB::sysDescr.0"};
   auto result_all = snmptranslate(args_all, "testing_snmptranslate_m_all");
   ASSERT_EQ(result_all.size(), 1u);
   EXPECT_EQ(result_all[0], ".1.3.6.1.2.1.1.1.0");

   std::vector<std::string> args_mod = {"-m", "SNMPv2-MIB", "-On", "SNMPv2-MIB::sysDescr.0"};
   auto result_mod = snmptranslate(args_mod, "testing_snmptranslate_m_mod");
   ASSERT_EQ(result_mod.size(), 1u);
   EXPECT_EQ(result_mod[0], ".1.3.6.1.2.1.1.1.0");
}

TEST_F(SnmpTranslateTest, TestMibDirectoryOption) {
   char const *mib_dir = netsnmp_get_mib_directory();
   ASSERT_NE(mib_dir, nullptr);
   std::vector<std::string> args = {"-M", mib_dir, "-On", "SNMPv2-MIB::sysDescr.0"};
   auto result = snmptranslate(args, "testing_snmptranslate_mibdir");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_EQ(result[0], ".1.3.6.1.2.1.1.1.0");
}

TEST_F(SnmpTranslateTest, TestDebugTokenOption) {
   std::vector<std::string> args = {"-D_ezsnmp_nonexistent_", "-On", "SNMPv2-MIB::sysDescr.0"};
   auto result = snmptranslate(args, "testing_snmptranslate_debug");
   snmp_set_do_debugging(0);
   ASSERT_EQ(result.size(), 1u);
   EXPECT_EQ(result[0], ".1.3.6.1.2.1.1.1.0");
}

TEST_F(SnmpTranslateTest, TestWidthOption) {
   std::vector<std::string> args = {"-w", "80", "-Td", "SNMPv2-MIB::sysDescr.0"};
   auto result = snmptranslate(args, "testing_snmptranslate_width");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_NE(result[0].find("sysDescr"), std::string::npos);
}

TEST_F(SnmpTranslateTest, TestParserOption) {
   std::vector<std::string> args = {"-Pc", "-On", "SNMPv2-MIB::sysDescr.0"};
   auto result = snmptranslate(args, "testing_snmptranslate_p_valid");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_EQ(result[0], ".1.3.6.1.2.1.1.1.0");

   std::vector<std::string> bad_args = {"-PX", "SNMPv2-MIB::sysDescr.0"};
   EXPECT_THROW(snmptranslate(bad_args, "testing_snmptranslate_p_invalid"), ParseErrorBase);
}

TEST_F(SnmpTranslateTest, TestInvalidOAndIOptionsThrowParseError) {
   std::vector<std::string> bad_o = {"-O?", "SNMPv2-MIB::sysDescr.0"};
   EXPECT_THROW(snmptranslate(bad_o, "testing_snmptranslate_o_invalid"), ParseErrorBase);

   std::vector<std::string> bad_i = {"-IX", "SNMPv2-MIB::sysDescr.0"};
   EXPECT_THROW(snmptranslate(bad_i, "testing_snmptranslate_i_invalid"), ParseErrorBase);
}

TEST_F(SnmpTranslateTest, TestLogOption) {
   std::vector<std::string> args = {"-Ln", "-On", "SNMPv2-MIB::sysDescr.0"};
   auto result = snmptranslate(args, "testing_snmptranslate_l_valid");
   ASSERT_EQ(result.size(), 1u);
   EXPECT_EQ(result[0], ".1.3.6.1.2.1.1.1.0");

   std::vector<std::string> bad_args = {"-LX", "SNMPv2-MIB::sysDescr.0"};
   EXPECT_THROW(snmptranslate(bad_args, "testing_snmptranslate_l_invalid"), ParseErrorBase);
}

TEST_F(SnmpTranslateTest, TestPrintReportsWithoutOid) {
   EXPECT_FALSE(snmptranslate({"-Tp"}, "testing_snmptranslate_tp_root")[0].empty());
   EXPECT_FALSE(snmptranslate({"-Ta"}, "testing_snmptranslate_ta_root")[0].empty());
   EXPECT_FALSE(snmptranslate({"-Tl"}, "testing_snmptranslate_tl")[0].empty());
   EXPECT_FALSE(snmptranslate({"-To"}, "testing_snmptranslate_to")[0].empty());
   EXPECT_FALSE(snmptranslate({"-Ts"}, "testing_snmptranslate_ts")[0].empty());
   EXPECT_FALSE(snmptranslate({"-Tt"}, "testing_snmptranslate_tt")[0].empty());
   EXPECT_FALSE(snmptranslate({"-Tz"}, "testing_snmptranslate_tz")[0].empty());
}

TEST_F(SnmpTranslateTest, TestPrintTreeUnknownNumericOidThrows) {
   std::vector<std::string> args = {"-Tp", ".99.99.99"};
   EXPECT_THROW(snmptranslate(args, "testing_snmptranslate_tp_unknown"), UnknownObjectIDErrorBase);
}
