#include <gtest/gtest.h>

#include <algorithm>
#include <functional>
#include <string>
#include <vector>

#include "exceptionsbase.h"
#include "sessionbase.h"

class SessionBaseCliOptionsTest : public ::testing::Test {};

TEST_F(SessionBaseCliOptionsTest, PrintOptionsConstructor) {
   SessionBase session(
       /* hostname */ "localhost",
       /* port_number */ "161",
       /* version */ "1",
       /* community */ "public",
       /* auth_protocol */ "",
       /* auth_passphrase */ "",
       /* security_engine_id */ "",
       /* context_engine_id */ "",
       /* security_level */ "",
       /* context */ "",
       /* security_username */ "",
       /* privacy_protocol */ "",
       /* privacy_passphrase */ "",
       /* boots_time */ "",
       /* retries */ "",
       /* timeout */ "",
       /* load_mibs */ "",
       /* mib_directories */ "",
       /* print_enums_numerically */ true,
       /* print_full_oids */ true,
       /* print_oids_numerically */ true,
       /* print_timeticks_numerically */ true,
       /* print_hex_strings */ true);
   auto args = session._get_args();
   std::vector<std::string> expected = {"-c", "public", "-v", "1", "-O", "e", "-O",           "f",
                                        "-O", "n",      "-O", "t", "-O", "x", "localhost:161"};
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseCliOptionsTest, MaxRepeatersConstructorParam) {
   SessionBase session(
       /* hostname */ "localhost",
       /* port_number */ "161",
       /* version */ "2c",
       /* community */ "public",
       /* auth_protocol */ "",
       /* auth_passphrase */ "",
       /* security_engine_id */ "",
       /* context_engine_id */ "",
       /* security_level */ "",
       /* context */ "",
       /* security_username */ "",
       /* privacy_protocol */ "",
       /* privacy_passphrase */ "",
       /* boots_time */ "",
       /* retries */ "",
       /* timeout */ "",
       /* load_mibs */ "",
       /* mib_directories */ "",
       /* print_enums_numerically */ false,
       /* print_full_oids */ false,
       /* print_oids_numerically */ false,
       /* print_timeticks_numerically */ false,
       /* print_hex_strings */ false,
       /* set_max_repeaters_to_num */ "25");

   auto args = session._get_args();
   EXPECT_NE(std::find(args.begin(), args.end(), "-Cr25"), args.end());
}

struct PrintOptionSetterCase {
   std::string name;
   std::function<void(SessionBase&, bool)> setter;
   std::function<bool(SessionBase const&)> getter;
};

class SessionBasePrintOptionSetterTest : public ::testing::TestWithParam<PrintOptionSetterCase> {};

TEST_P(SessionBasePrintOptionSetterTest, TogglesOutputFlag) {
   PrintOptionSetterCase const& tc = GetParam();
   SessionBase session("localhost", "161", "2c", "public");

   tc.setter(session, true);
   EXPECT_TRUE(tc.getter(session));
   auto args_on = session._get_args();
   EXPECT_NE(std::find(args_on.begin(), args_on.end(), "-O"), args_on.end());

   tc.setter(session, false);
   EXPECT_FALSE(tc.getter(session));
   auto args_off = session._get_args();
   EXPECT_EQ(std::find(args_off.begin(), args_off.end(), "-O"), args_off.end());
   EXPECT_GT(args_on.size(), args_off.size());
}

INSTANTIATE_TEST_SUITE_P(
    PrintOptionSetters,
    SessionBasePrintOptionSetterTest,
    ::testing::Values(
        PrintOptionSetterCase{
            "PrintEnumsNumerically",
            [](SessionBase& s, bool v) { s._set_print_enums_numerically(v); },
            [](SessionBase const& s) { return s._get_print_enums_numerically(); }},
        PrintOptionSetterCase{"PrintFullOids",
                              [](SessionBase& s, bool v) { s._set_print_full_oids(v); },
                              [](SessionBase const& s) { return s._get_print_full_oids(); }},
        PrintOptionSetterCase{"PrintOidsNumerically",
                              [](SessionBase& s, bool v) { s._set_print_oids_numerically(v); },
                              [](SessionBase const& s) { return s._get_print_oids_numerically(); }},
        PrintOptionSetterCase{
            "PrintTimeticksNumerically",
            [](SessionBase& s, bool v) { s._set_print_timeticks_numerically(v); },
            [](SessionBase const& s) { return s._get_print_timeticks_numerically(); }},
        PrintOptionSetterCase{"PrintHexStrings",
                              [](SessionBase& s, bool v) { s._set_print_hex_strings(v); },
                              [](SessionBase const& s) { return s._get_print_hex_strings(); }}),
    [](testing::TestParamInfo<PrintOptionSetterCase> const& info) { return info.param.name; });

struct MibSetterCase {
   std::string name;
   std::string flag;
   std::string value;
   std::function<void(SessionBase&, std::string const&)> setter;
};

class SessionBaseMibSetterTest : public ::testing::TestWithParam<MibSetterCase> {};

TEST_P(SessionBaseMibSetterTest, SetsAndClearsFlag) {
   MibSetterCase const& tc = GetParam();
   SessionBase session("localhost", "161", "2c", "public");

   tc.setter(session, tc.value);
   auto args = session._get_args();
   EXPECT_NE(std::find(args.begin(), args.end(), tc.flag), args.end());

   tc.setter(session, "");
   args = session._get_args();
   EXPECT_EQ(std::find(args.begin(), args.end(), tc.flag), args.end());
}

INSTANTIATE_TEST_SUITE_P(
    MibSetters,
    SessionBaseMibSetterTest,
    ::testing::Values(
        MibSetterCase{"LoadMibs", "-m", "ALL",
                      [](SessionBase& s, std::string const& v) { s._set_load_mibs(v); }},
        MibSetterCase{"MibDirectories", "-M", "/usr/share/snmp/mibs",
                      [](SessionBase& s, std::string const& v) { s._set_mib_directories(v); }}),
    [](testing::TestParamInfo<MibSetterCase> const& info) { return info.param.name; });

TEST_F(SessionBaseCliOptionsTest, MaxRepeatersToNumSetter) {
   SessionBase session("localhost", "161", "2c", "public");

   session._set_max_repeaters_to_num("50");
   auto args = session._get_args();
   EXPECT_NE(std::find(args.begin(), args.end(), "-Cr50"), args.end());
}

TEST_F(SessionBaseCliOptionsTest, NewCliOptionsDefaults) {
   SessionBase session;

   EXPECT_FALSE(session._get_print_oid_suffix_only());
   EXPECT_FALSE(session._get_print_oid_module_name());
   EXPECT_FALSE(session._get_print_oid_ucd_style());
   EXPECT_FALSE(session._get_print_ascii_strings());
   EXPECT_FALSE(session._get_print_leading_zero_hex());
   EXPECT_FALSE(session._get_print_hex_text());
   EXPECT_FALSE(session._get_dont_breakdown_oids());
   EXPECT_FALSE(session._get_escape_quotes_in_indexes());
   EXPECT_FALSE(session._get_extended_index_format());
   EXPECT_FALSE(session._get_dont_print_units());
   EXPECT_EQ(session._get_output_precision(), "");

   EXPECT_FALSE(session._get_regex_oid_matching());
   EXPECT_FALSE(session._get_ignore_display_hints());
   EXPECT_FALSE(session._get_dont_check_range());
   EXPECT_FALSE(session._get_random_access_oid());
   EXPECT_FALSE(session._get_read_ucd_style_oid());
   EXPECT_EQ(session._get_oid_suffix(), "");
   EXPECT_EQ(session._get_oid_prefix(), "");

   EXPECT_FALSE(session._get_mib_allow_underline());
   EXPECT_FALSE(session._get_mib_comment_to_eol());
   EXPECT_FALSE(session._get_mib_replace_with_latest());

   EXPECT_EQ(session._get_non_repeaters(), "");
   EXPECT_FALSE(session._get_walk_dont_check_lexicographic());
   EXPECT_FALSE(session._get_walk_include_requested());
   EXPECT_FALSE(session._get_walk_dont_get_requested());
   EXPECT_EQ(session._get_walk_end_oid(), "");
   EXPECT_FALSE(session._get_dont_fix_pdus());
}

TEST_F(SessionBaseCliOptionsTest, NewCliOptionsConstructorAndArgs) {
   SessionBase session("localhost", "161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "1", "", "", false, false, false, false, false, "10", true, true, true,
                       true, true, true, true, true, true, true, "%.2f", true, true, true, true,
                       true, ".1", ".iso", true, true, true, "2", true, true, true, "1.3.6.1.2.1.2",
                       true);

   EXPECT_TRUE(session._get_print_oid_suffix_only());
   EXPECT_TRUE(session._get_print_oid_module_name());
   EXPECT_TRUE(session._get_print_oid_ucd_style());
   EXPECT_TRUE(session._get_print_ascii_strings());
   EXPECT_TRUE(session._get_print_leading_zero_hex());
   EXPECT_TRUE(session._get_print_hex_text());
   EXPECT_TRUE(session._get_dont_breakdown_oids());
   EXPECT_TRUE(session._get_escape_quotes_in_indexes());
   EXPECT_TRUE(session._get_extended_index_format());
   EXPECT_TRUE(session._get_dont_print_units());
   EXPECT_EQ(session._get_output_precision(), "%.2f");
   EXPECT_TRUE(session._get_regex_oid_matching());
   EXPECT_TRUE(session._get_ignore_display_hints());
   EXPECT_TRUE(session._get_dont_check_range());
   EXPECT_TRUE(session._get_random_access_oid());
   EXPECT_TRUE(session._get_read_ucd_style_oid());
   EXPECT_EQ(session._get_oid_suffix(), ".1");
   EXPECT_EQ(session._get_oid_prefix(), ".iso");
   EXPECT_TRUE(session._get_mib_allow_underline());
   EXPECT_TRUE(session._get_mib_comment_to_eol());
   EXPECT_TRUE(session._get_mib_replace_with_latest());
   EXPECT_EQ(session._get_non_repeaters(), "2");
   EXPECT_TRUE(session._get_walk_dont_check_lexicographic());
   EXPECT_TRUE(session._get_walk_include_requested());
   EXPECT_TRUE(session._get_walk_dont_get_requested());
   EXPECT_EQ(session._get_walk_end_oid(), "1.3.6.1.2.1.2");
   EXPECT_TRUE(session._get_dont_fix_pdus());

   auto const& args = session._get_args();
   auto has_pair = [&args](std::string const& a, std::string const& b) {
      for (size_t i = 0; i + 1 < args.size(); ++i) {
         if (args[i] == a && args[i + 1] == b) {
            return true;
         }
      }
      return false;
   };
   auto has_single = [&args](std::string const& a) {
      return std::find(args.begin(), args.end(), a) != args.end();
   };

   EXPECT_TRUE(has_pair("-O", "s"));
   EXPECT_TRUE(has_pair("-O", "S"));
   EXPECT_TRUE(has_pair("-O", "u"));
   EXPECT_TRUE(has_pair("-O", "a"));
   EXPECT_TRUE(has_pair("-O", "0"));
   EXPECT_TRUE(has_pair("-O", "T"));
   EXPECT_TRUE(has_pair("-O", "b"));
   EXPECT_TRUE(has_pair("-O", "E"));
   EXPECT_TRUE(has_pair("-O", "X"));
   EXPECT_TRUE(has_pair("-O", "U"));
   EXPECT_TRUE(has_pair("-Op", "%.2f"));
   EXPECT_TRUE(has_pair("-I", "b"));
   EXPECT_TRUE(has_pair("-I", "h"));
   EXPECT_TRUE(has_pair("-I", "r"));
   EXPECT_TRUE(has_pair("-I", "R"));
   EXPECT_TRUE(has_pair("-I", "u"));
   EXPECT_TRUE(has_pair("-Is", ".1"));
   EXPECT_TRUE(has_pair("-IS", ".iso"));
   EXPECT_TRUE(has_pair("-P", "u"));
   EXPECT_TRUE(has_pair("-P", "c"));
   EXPECT_TRUE(has_pair("-P", "R"));
   EXPECT_TRUE(has_single("-Cr10"));
   EXPECT_TRUE(has_single("-Cn2"));
   EXPECT_TRUE(has_single("-Cc"));
   EXPECT_TRUE(has_single("-Ci"));
   EXPECT_TRUE(has_single("-CI"));
   EXPECT_TRUE(has_pair("-CE", "1.3.6.1.2.1.2"));
   EXPECT_TRUE(has_single("-Cf"));
}

TEST_F(SessionBaseCliOptionsTest, NewCliOptionsSetters) {
   SessionBase session("localhost", "161", "2c", "public");

   session._set_print_oid_suffix_only(true);
   session._set_print_oid_module_name(true);
   session._set_print_oid_ucd_style(true);
   session._set_print_ascii_strings(true);
   session._set_print_leading_zero_hex(true);
   session._set_print_hex_text(true);
   session._set_dont_breakdown_oids(true);
   session._set_escape_quotes_in_indexes(true);
   session._set_extended_index_format(true);
   session._set_dont_print_units(true);
   session._set_output_precision("%.3f");
   session._set_regex_oid_matching(true);
   session._set_ignore_display_hints(true);
   session._set_dont_check_range(true);
   session._set_random_access_oid(true);
   session._set_read_ucd_style_oid(true);
   session._set_oid_suffix(".0");
   session._set_oid_prefix(".1.3");
   session._set_mib_allow_underline(true);
   session._set_mib_comment_to_eol(true);
   session._set_mib_replace_with_latest(true);
   session._set_non_repeaters("4");
   session._set_walk_dont_check_lexicographic(true);
   session._set_walk_include_requested(true);
   session._set_walk_dont_get_requested(true);
   session._set_walk_end_oid(".1.3.6.1");
   session._set_dont_fix_pdus(true);

   EXPECT_TRUE(session._get_print_oid_suffix_only());
   EXPECT_TRUE(session._get_print_oid_module_name());
   EXPECT_TRUE(session._get_print_oid_ucd_style());
   EXPECT_TRUE(session._get_print_ascii_strings());
   EXPECT_TRUE(session._get_print_leading_zero_hex());
   EXPECT_TRUE(session._get_print_hex_text());
   EXPECT_TRUE(session._get_dont_breakdown_oids());
   EXPECT_TRUE(session._get_escape_quotes_in_indexes());
   EXPECT_TRUE(session._get_extended_index_format());
   EXPECT_TRUE(session._get_dont_print_units());
   EXPECT_EQ(session._get_output_precision(), "%.3f");
   EXPECT_TRUE(session._get_regex_oid_matching());
   EXPECT_TRUE(session._get_ignore_display_hints());
   EXPECT_TRUE(session._get_dont_check_range());
   EXPECT_TRUE(session._get_random_access_oid());
   EXPECT_TRUE(session._get_read_ucd_style_oid());
   EXPECT_EQ(session._get_oid_suffix(), ".0");
   EXPECT_EQ(session._get_oid_prefix(), ".1.3");
   EXPECT_TRUE(session._get_mib_allow_underline());
   EXPECT_TRUE(session._get_mib_comment_to_eol());
   EXPECT_TRUE(session._get_mib_replace_with_latest());
   EXPECT_EQ(session._get_non_repeaters(), "4");
   EXPECT_TRUE(session._get_walk_dont_check_lexicographic());
   EXPECT_TRUE(session._get_walk_include_requested());
   EXPECT_TRUE(session._get_walk_dont_get_requested());
   EXPECT_EQ(session._get_walk_end_oid(), ".1.3.6.1");
   EXPECT_TRUE(session._get_dont_fix_pdus());

   auto const& args = session._get_args();
   EXPECT_NE(std::find(args.begin(), args.end(), "-Cn4"), args.end());
   EXPECT_NE(std::find(args.begin(), args.end(), "-Cf"), args.end());
   EXPECT_NE(std::find(args.begin(), args.end(), "-Op"), args.end());
}

struct ScopedCFlagsCase {
   std::string name;
   std::string target_oid;
   std::function<void(SessionBase&, std::string const&)> invoke;
   std::vector<std::string> expected_present;
   std::vector<std::string> expected_absent;
};

class SessionBaseOperationScopedCFlagsTest : public ::testing::TestWithParam<ScopedCFlagsCase> {};

TEST_P(SessionBaseOperationScopedCFlagsTest, ScopesCFlagsWithoutParseError) {
   ScopedCFlagsCase const& tc = GetParam();
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "0", "1");
   session._set_max_repeaters_to_num("5");
   session._set_non_repeaters("1");
   session._set_walk_dont_check_lexicographic(true);
   session._set_walk_include_requested(true);
   session._set_walk_dont_get_requested(true);
   session._set_walk_end_oid(".1.3.6.1.2.1.2");
   session._set_dont_fix_pdus(true);

   try {
      tc.invoke(session, tc.target_oid);
   } catch (ParseErrorBase const& e) {
      FAIL() << tc.name << " threw ParseErrorBase: " << e.what();
   } catch (std::exception const&) {
   }

   auto const& args = session._get_args();
   auto has_arg = [&args](std::string const& flag) {
      return std::find(args.begin(), args.end(), flag) != args.end();
   };

   for (auto const& flag : tc.expected_present) {
      EXPECT_TRUE(has_arg(flag)) << "Expected flag present: " << flag;
   }
   for (auto const& flag : tc.expected_absent) {
      EXPECT_FALSE(has_arg(flag)) << "Expected flag absent: " << flag;
   }
}

INSTANTIATE_TEST_SUITE_P(
    OperationScopedCFlags,
    SessionBaseOperationScopedCFlagsTest,
    ::testing::Values(
        ScopedCFlagsCase{"Get",
                         ".1.3.6.1.2.1.1.1.0",
                         [](SessionBase& s, std::string const& oid) { (void)s.get(oid); },
                         {"-Cf"},
                         {"-Cr5", "-Cn1", "-Cc"}},
        ScopedCFlagsCase{"Walk",
                         ".1.3.6.1.2.1.1",
                         [](SessionBase& s, std::string const& oid) { (void)s.walk(oid); },
                         {"-Cc", "-Ci", "-CI", "-CE"},
                         {"-Cr5", "-Cf"}},
        ScopedCFlagsCase{"BulkGet",
                         ".1.3.6.1.2.1.1.1.0",
                         [](SessionBase& s, std::string const& oid) { (void)s.bulk_get(oid); },
                         {"-Cr5", "-Cn1"},
                         {"-Cc", "-Cf"}},
        ScopedCFlagsCase{"BulkWalk",
                         ".1.3.6.1.2.1.1",
                         [](SessionBase& s, std::string const& oid) { (void)s.bulk_walk(oid); },
                         {"-Cr5", "-Cn1", "-Cc", "-Ci"},
                         {"-CI", "-CE", "-Cf"}}),
    [](testing::TestParamInfo<ScopedCFlagsCase> const& info) { return info.param.name; });
