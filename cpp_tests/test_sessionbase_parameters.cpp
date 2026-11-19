#include <gtest/gtest.h>

#include <algorithm>
#include <functional>
#include <optional>
#include <string>
#include <tuple>
#include <vector>

#include "exceptionsbase.h"
#include "sessionbase.h"

struct PrintOptions {
   bool print_enums_numerically;
   bool print_full_oids;
   bool print_oids_numerically;
   bool print_timeticks_numerically;
   bool print_hex_strings;
   std::vector<std::string> expected_flags;
};

using SessionParam = std::tuple<std::string, PrintOptions>;

class SessionsParamTest : public ::testing::TestWithParam<SessionParam> {};

static std::vector<std::string> build_expected_args(std::string const& version,
                                                    PrintOptions const& options) {
   std::vector<std::string> args;
   if (version != "3") {
      args.push_back("-c");
      args.push_back("public");
   }
   args.push_back("-v");
   args.push_back(version);
   for (auto const& flag : options.expected_flags) {
      args.push_back("-O");
      args.push_back(flag);
   }
   args.push_back("localhost:161");
   return args;
}

TEST_P(SessionsParamTest, PrintOptionsAreAppliedToArgs) {
   auto const& [version, options] = GetParam();

   SessionBase session("localhost", "161", version, "public", "", "", "", "", "", "", "", "", "",
                       "", "", "", "", "", options.print_enums_numerically, options.print_full_oids,
                       options.print_oids_numerically, options.print_timeticks_numerically,
                       options.print_hex_strings);

   auto args = session._get_args();
   auto expected = build_expected_args(version, options);
   EXPECT_EQ(args, expected);
}

// --- Integration tests to verify print options affect actual SNMP output ---

// Helper to safely get a single OID and either return the first result or indicate no data.
static std::optional<Result> GetSingleOidOrSkip(bool print_enums,
                                                bool print_full,
                                                bool print_oids_num,
                                                bool print_timeticks_num,
                                                std::string const& mib_oid) {
   SessionBase session(
       /* hostname */ "localhost",
       /* port_number */ "11161",
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
       /* retries */ "3",
       /* timeout */ "5",
       /* load_mibs */ "",
       /* mib_directories */ "",
       /* print_enums_numerically */ print_enums,
       /* print_full_oids */ print_full,
       /* print_oids_numerically */ print_oids_num,
       /* print_timeticks_numerically */ print_timeticks_num);

   auto result = session.get(mib_oid);
   if (result.empty()) {
      return std::nullopt;
   }
   return result.front();
}

// Macro for skipping tests when no data is available, compatible with older GTest
// WARNING: This macro causes the calling function to return early.
// Use only at function scope, not inside loops or other control structures.
#if defined(GTEST_SKIP)
#define EZSNMP_SKIP_TEST_AND_RETURN_IF_NO_DATA(msg) GTEST_SKIP() << msg
#else
#define EZSNMP_SKIP_TEST_AND_RETURN_IF_NO_DATA(msg) \
   do {                                             \
      std::cout << "SKIPPED: " << msg << std::endl; \
      return;                                       \
   } while (0)
#endif

TEST(SessionBaseParametersIntegration, TimeticksNumericFlagChangesValueFormat) {
   // With print_timeticks_numerically = false: value is human-friendly (e.g., "X days, ...")
   auto r_text_opt = GetSingleOidOrSkip(/*enums*/ false, /*full*/ false, /*oids_num*/ false,
                                        /*timeticks_num*/ false, "SNMPv2-MIB::sysUpTime.0");
   if (!r_text_opt.has_value()) {
      EZSNMP_SKIP_TEST_AND_RETURN_IF_NO_DATA(
          "SNMP agent returned no data for OID: SNMPv2-MIB::sysUpTime.0");
   }
   auto r_text = *r_text_opt;
   EXPECT_NE(r_text.type.find("Timeticks"), std::string::npos);
   // Heuristic: textual timeticks usually contain a space or comma
   bool looks_textual = (r_text.value.find(" ") != std::string::npos) ||
                        (r_text.value.find(",") != std::string::npos) ||
                        (r_text.value.find("milli-seconds") != std::string::npos);
   EXPECT_TRUE(looks_textual) << "Expected non-numeric timeticks representation, got: "
                              << r_text.value;

   // With print_timeticks_numerically = true: value should be purely numeric
   auto r_num_opt = GetSingleOidOrSkip(/*enums*/ false, /*full*/ false, /*oids_num*/ false,
                                       /*timeticks_num*/ true, "SNMPv2-MIB::sysUpTime.0");
   if (!r_num_opt.has_value()) {
      EZSNMP_SKIP_TEST_AND_RETURN_IF_NO_DATA(
          "SNMP agent returned no data for OID: SNMPv2-MIB::sysUpTime.0");
   }
   auto r_num = *r_num_opt;
   EXPECT_NE(r_num.type.find("Timeticks"), std::string::npos);
   // Check value is digits only
   bool all_digits =
       !r_num.value.empty() && std::all_of(r_num.value.begin(), r_num.value.end(), ::isdigit);
   EXPECT_TRUE(all_digits) << "Expected numeric timeticks, got: " << r_num.value;
}

TEST(SessionBaseParametersIntegration, OidsNumericFlagChangesOidFormat) {
   // Without numeric OIDs: expect textual module name in oid string
   auto r_text_opt2 = GetSingleOidOrSkip(/*enums*/ false, /*full*/ false, /*oids_num*/ false,
                                         /*timeticks_num*/ false, "SNMPv2-MIB::sysUpTime.0");
   if (!r_text_opt2.has_value()) {
      EZSNMP_SKIP_TEST_AND_RETURN_IF_NO_DATA(
          "SNMP agent returned no data for OID: SNMPv2-MIB::sysUpTime.0");
   }
   auto r_text = *r_text_opt2;
   std::string oid_text = r_text.oid;
   bool has_module = (oid_text.find("SNMPv2-MIB") != std::string::npos) ||
                     (oid_text.find("::") != std::string::npos);
   EXPECT_TRUE(has_module) << "Expected textual OID, got: " << oid_text;

   // With numeric OIDs: expect dotted numeric form, avoid module markers
   auto r_num_opt2 = GetSingleOidOrSkip(/*enums*/ false, /*full*/ false, /*oids_num*/ true,
                                        /*timeticks_num*/ false, "SNMPv2-MIB::sysUpTime.0");
   if (!r_num_opt2.has_value()) {
      EZSNMP_SKIP_TEST_AND_RETURN_IF_NO_DATA(
          "SNMP agent returned no data for OID: SNMPv2-MIB::sysUpTime.0");
   }
   auto r_num = *r_num_opt2;
   std::string oid_num = r_num.oid;
   bool dotted_numeric = !oid_num.empty() && oid_num.find("::") == std::string::npos &&
                         std::count(oid_num.begin(), oid_num.end(), '.') >= 3;
   EXPECT_TRUE(dotted_numeric) << "Expected numeric/dotted OID, got: " << oid_num;
}

static auto const SESSION_PARAM_VALUES =
    testing::Combine(testing::Values(std::string("1"), std::string("2c"), std::string("3")),
                     testing::Values(PrintOptions{false, false, false, false, false, {}},
                                     PrintOptions{true, false, false, false, false, {"e"}},
                                     PrintOptions{false, true, false, false, false, {"f"}},
                                     PrintOptions{false, false, true, false, false, {"n"}},
                                     PrintOptions{true, true, false, false, false, {"e", "f"}},
                                     PrintOptions{true, false, true, false, false, {"e", "n"}},
                                     PrintOptions{false, true, true, false, false, {"f", "n"}},
                                     PrintOptions{true, true, true, false, false, {"e", "f", "n"}},
                                     PrintOptions{false, false, false, true, false, {"t"}},
                                     PrintOptions{false, false, false, false, true, {"x"}}));

#if defined(INSTANTIATE_TEST_SUITE_P)
INSTANTIATE_TEST_SUITE_P(SessionVersions,
                         SessionsParamTest,
                         SESSION_PARAM_VALUES,
                         [](testing::TestParamInfo<SessionParam> const& info) {
                            auto const& opts = std::get<1>(info.param);
                            std::string name = "v" + std::get<0>(info.param);
                            for (auto const& f : opts.expected_flags) {
                               name += "_" + f;
                            }
                            if (opts.expected_flags.empty()) {
                               name += "_none";
                            }
                            return name;
                         });
#else
// For legacy INSTANTIATE_TEST_CASE_P, wrap the cartesian product in Values()
INSTANTIATE_TEST_CASE_P(
    SessionVersions,
    SessionsParamTest,
    testing::Values(
        std::make_tuple(std::string("1"), PrintOptions{false, false, false, false, false, {}}),
        std::make_tuple(std::string("1"), PrintOptions{true, false, false, false, false, {"e"}}),
        std::make_tuple(std::string("1"), PrintOptions{false, true, false, false, false, {"f"}}),
        std::make_tuple(std::string("1"), PrintOptions{false, false, true, false, false, {"n"}}),
        std::make_tuple(std::string("1"),
                        PrintOptions{true, true, false, false, false, {"e", "f"}}),
        std::make_tuple(std::string("1"),
                        PrintOptions{true, false, true, false, false, {"e", "n"}}),
        std::make_tuple(std::string("1"),
                        PrintOptions{false, true, true, false, false, {"f", "n"}}),
        std::make_tuple(std::string("1"),
                        PrintOptions{true, true, true, false, false, {"e", "f", "n"}}),
        std::make_tuple(std::string("1"), PrintOptions{false, false, false, true, false, {"t"}}),
        std::make_tuple(std::string("1"), PrintOptions{false, false, false, false, true, {"x"}}),
        std::make_tuple(std::string("2c"), PrintOptions{false, false, false, false, false, {}}),
        std::make_tuple(std::string("2c"), PrintOptions{true, false, false, false, false, {"e"}}),
        std::make_tuple(std::string("2c"), PrintOptions{false, true, false, false, false, {"f"}}),
        std::make_tuple(std::string("2c"), PrintOptions{false, false, true, false, false, {"n"}}),
        std::make_tuple(std::string("2c"),
                        PrintOptions{true, true, false, false, false, {"e", "f"}}),
        std::make_tuple(std::string("2c"),
                        PrintOptions{true, false, true, false, false, {"e", "n"}}),
        std::make_tuple(std::string("2c"),
                        PrintOptions{false, true, true, false, false, {"f", "n"}}),
        std::make_tuple(std::string("2c"),
                        PrintOptions{true, true, true, false, false, {"e", "f", "n"}}),
        std::make_tuple(std::string("2c"), PrintOptions{false, false, false, true, false, {"t"}}),
        std::make_tuple(std::string("2c"), PrintOptions{false, false, false, false, true, {"x"}}),
        std::make_tuple(std::string("3"), PrintOptions{false, false, false, false, false, {}}),
        std::make_tuple(std::string("3"), PrintOptions{true, false, false, false, false, {"e"}}),
        std::make_tuple(std::string("3"), PrintOptions{false, true, false, false, false, {"f"}}),
        std::make_tuple(std::string("3"), PrintOptions{false, false, true, false, false, {"n"}}),
        std::make_tuple(std::string("3"),
                        PrintOptions{true, true, false, false, false, {"e", "f"}}),
        std::make_tuple(std::string("3"),
                        PrintOptions{true, false, true, false, false, {"e", "n"}}),
        std::make_tuple(std::string("3"),
                        PrintOptions{false, true, true, false, false, {"f", "n"}}),
        std::make_tuple(std::string("3"),
                        PrintOptions{true, true, true, false, false, {"e", "f", "n"}}),
        std::make_tuple(std::string("3"), PrintOptions{false, false, false, true, false, {"t"}}),
        std::make_tuple(std::string("3"), PrintOptions{false, false, false, false, true, {"x"}})));
#endif

struct ExtendedCliOptionCase {
   std::string name;
   std::function<void(SessionBase&)> apply;
   std::vector<std::string> expected_tokens;
};

class ExtendedCliOptionsParamTest : public ::testing::TestWithParam<ExtendedCliOptionCase> {};

TEST_P(ExtendedCliOptionsParamTest, OptionPopulatesExpectedArgs) {
   auto const& param = GetParam();
   SessionBase session("localhost", "161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "", "");
   param.apply(session);
   auto const& args = session._get_args();
   for (auto const& token : param.expected_tokens) {
      EXPECT_NE(std::find(args.begin(), args.end(), token), args.end())
          << "Missing expected token '" << token << "' for case " << param.name;
   }
   EXPECT_EQ(args.back(), "localhost:161");
}

INSTANTIATE_TEST_SUITE_P(
    ExtendedCliOptions,
    ExtendedCliOptionsParamTest,
    testing::Values(
        ExtendedCliOptionCase{"print_oid_suffix_only",
                              [](SessionBase& s) { s._set_print_oid_suffix_only(true); },
                              {"-O", "s"}},
        ExtendedCliOptionCase{"print_oid_module_name",
                              [](SessionBase& s) { s._set_print_oid_module_name(true); },
                              {"-O", "S"}},
        ExtendedCliOptionCase{"print_oid_ucd_style",
                              [](SessionBase& s) { s._set_print_oid_ucd_style(true); },
                              {"-O", "u"}},
        ExtendedCliOptionCase{"print_ascii_strings",
                              [](SessionBase& s) { s._set_print_ascii_strings(true); },
                              {"-O", "a"}},
        ExtendedCliOptionCase{"print_leading_zero_hex",
                              [](SessionBase& s) { s._set_print_leading_zero_hex(true); },
                              {"-O", "0"}},
        ExtendedCliOptionCase{
            "print_hex_text", [](SessionBase& s) { s._set_print_hex_text(true); }, {"-O", "T"}},
        ExtendedCliOptionCase{"dont_breakdown_oids",
                              [](SessionBase& s) { s._set_dont_breakdown_oids(true); },
                              {"-O", "b"}},
        ExtendedCliOptionCase{"escape_quotes_in_indexes",
                              [](SessionBase& s) { s._set_escape_quotes_in_indexes(true); },
                              {"-O", "E"}},
        ExtendedCliOptionCase{"extended_index_format",
                              [](SessionBase& s) { s._set_extended_index_format(true); },
                              {"-O", "X"}},
        ExtendedCliOptionCase{
            "dont_print_units", [](SessionBase& s) { s._set_dont_print_units(true); }, {"-O", "U"}},
        ExtendedCliOptionCase{"output_precision",
                              [](SessionBase& s) { s._set_output_precision("%.2f"); },
                              {"-Op", "%.2f"}},
        ExtendedCliOptionCase{"regex_oid_matching",
                              [](SessionBase& s) { s._set_regex_oid_matching(true); },
                              {"-I", "b"}},
        ExtendedCliOptionCase{"ignore_display_hints",
                              [](SessionBase& s) { s._set_ignore_display_hints(true); },
                              {"-I", "h"}},
        ExtendedCliOptionCase{
            "dont_check_range", [](SessionBase& s) { s._set_dont_check_range(true); }, {"-I", "r"}},
        ExtendedCliOptionCase{"random_access_oid",
                              [](SessionBase& s) { s._set_random_access_oid(true); },
                              {"-I", "R"}},
        ExtendedCliOptionCase{"read_ucd_style_oid",
                              [](SessionBase& s) { s._set_read_ucd_style_oid(true); },
                              {"-I", "u"}},
        ExtendedCliOptionCase{
            "oid_suffix", [](SessionBase& s) { s._set_oid_suffix(".0"); }, {"-Is", ".0"}},
        ExtendedCliOptionCase{
            "oid_prefix", [](SessionBase& s) { s._set_oid_prefix(".iso"); }, {"-IS", ".iso"}},
        ExtendedCliOptionCase{"mib_allow_underline",
                              [](SessionBase& s) { s._set_mib_allow_underline(true); },
                              {"-P", "u"}},
        ExtendedCliOptionCase{"mib_comment_to_eol",
                              [](SessionBase& s) { s._set_mib_comment_to_eol(true); },
                              {"-P", "c"}},
        ExtendedCliOptionCase{"mib_replace_with_latest",
                              [](SessionBase& s) { s._set_mib_replace_with_latest(true); },
                              {"-P", "R"}},
        ExtendedCliOptionCase{
            "non_repeaters", [](SessionBase& s) { s._set_non_repeaters("3"); }, {"-Cn3"}},
        ExtendedCliOptionCase{"walk_dont_check_lexicographic",
                              [](SessionBase& s) { s._set_walk_dont_check_lexicographic(true); },
                              {"-Cc"}},
        ExtendedCliOptionCase{"walk_include_requested",
                              [](SessionBase& s) { s._set_walk_include_requested(true); },
                              {"-Ci"}},
        ExtendedCliOptionCase{"walk_dont_get_requested",
                              [](SessionBase& s) { s._set_walk_dont_get_requested(true); },
                              {"-CI"}},
        ExtendedCliOptionCase{
            "walk_end_oid", [](SessionBase& s) { s._set_walk_end_oid("1.3.6"); }, {"-CE", "1.3.6"}},
        ExtendedCliOptionCase{
            "dont_fix_pdus", [](SessionBase& s) { s._set_dont_fix_pdus(true); }, {"-Cf"}}),
    [](testing::TestParamInfo<ExtendedCliOptionCase> const& info) { return info.param.name; });

TEST(SessionBaseGroupedConstructorTest, DefaultsPreservedWithEmptyMaps) {
   SessionBase session(std::map<std::string, std::string>{});
   EXPECT_EQ(session._get_hostname(), "localhost");
   EXPECT_EQ(session._get_port_number(), "");
   EXPECT_EQ(session._get_version(), "3");
   EXPECT_EQ(session._get_community(), "public");
   EXPECT_EQ(session._get_retries(), "3");
   EXPECT_EQ(session._get_timeout(), "1");
   EXPECT_FALSE(session._get_print_enums_numerically());
   EXPECT_FALSE(session._get_dont_fix_pdus());
}

TEST(SessionBaseGroupedConstructorTest, PopulatesAllFourOptionGroups) {
   SessionBase session({{"hostname", "127.0.0.1"},
                        {"port_number", "1161"},
                        {"version", "3"},
                        {"community", "private"},
                        {"retries", "5"},
                        {"timeout", "2"}},
                       {{"auth_protocol", "SHA"},
                        {"auth_passphrase", "authpass"},
                        {"security_engine_id", "800000020109840301"},
                        {"context_engine_id", "800000020109840302"},
                        {"security_level", "authPriv"},
                        {"context", "ctx1"},
                        {"security_username", "bert"},
                        {"privacy_protocol", "AES"},
                        {"privacy_passphrase", "privpass"},
                        {"boots_time", "10,20"}},
                       {{"load_mibs", "IF-MIB"},
                        {"mib_directories", "/usr/share/snmp/mibs"},
                        {"print_enums_numerically", "true"},
                        {"print_full_oids", "1"},
                        {"print_oids_numerically", "yes"},
                        {"output_precision", "%.2f"},
                        {"mib_allow_underline", "TRUE"},
                        {"dont_print_units", "false"}},
                       {{"set_max_repeaters_to_num", "25"},
                        {"non_repeaters", "2"},
                        {"walk_dont_check_lexicographic", "true"},
                        {"walk_end_oid", "1.3.6.1.2.1.2"},
                        {"dont_fix_pdus", "1"}});

   EXPECT_EQ(session._get_hostname(), "127.0.0.1");
   EXPECT_EQ(session._get_port_number(), "1161");
   EXPECT_EQ(session._get_version(), "3");
   EXPECT_EQ(session._get_community(), "private");
   EXPECT_EQ(session._get_retries(), "5");
   EXPECT_EQ(session._get_timeout(), "2");
   EXPECT_EQ(session._get_auth_protocol(), "SHA");
   EXPECT_EQ(session._get_security_username(), "bert");
   EXPECT_EQ(session._get_privacy_protocol(), "AES");
   EXPECT_EQ(session._get_load_mibs(), "IF-MIB");
   EXPECT_TRUE(session._get_print_enums_numerically());
   EXPECT_TRUE(session._get_print_full_oids());
   EXPECT_TRUE(session._get_print_oids_numerically());
   EXPECT_FALSE(session._get_dont_print_units());
   EXPECT_EQ(session._get_output_precision(), "%.2f");
   EXPECT_TRUE(session._get_mib_allow_underline());
   EXPECT_EQ(session._get_set_max_repeaters_to_num(), "25");
   EXPECT_EQ(session._get_non_repeaters(), "2");
   EXPECT_TRUE(session._get_walk_dont_check_lexicographic());
   EXPECT_EQ(session._get_walk_end_oid(), "1.3.6.1.2.1.2");
   EXPECT_TRUE(session._get_dont_fix_pdus());
}

TEST(SessionBaseGroupedConstructorTest, ThrowsOnUnknownKeyOrInvalidBool) {
   EXPECT_THROW((SessionBase{std::map<std::string, std::string>{{"unknown_key", "val"}}}),
                std::invalid_argument);
   EXPECT_THROW((SessionBase{{}, {{"not_a_v3_key", "val"}}}), std::invalid_argument);
   EXPECT_THROW((SessionBase{{}, {}, {{"print_full_oids", "not_a_bool"}}}), std::invalid_argument);
   EXPECT_THROW((SessionBase{{}, {}, {}, {{"bad_op_key", "1"}}}), std::invalid_argument);
}
