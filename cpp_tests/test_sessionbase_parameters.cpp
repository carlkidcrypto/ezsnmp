#include <gtest/gtest.h>

#include <algorithm>
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
                       options.print_oids_numerically, options.print_timeticks_numerically);

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
                     testing::Values(PrintOptions{false, false, false, false, {}},
                                     PrintOptions{true, false, false, false, {"e"}},
                                     PrintOptions{false, true, false, false, {"f"}},
                                     PrintOptions{false, false, true, false, {"n"}},
                                     PrintOptions{true, true, false, false, {"e", "f"}},
                                     PrintOptions{true, false, true, false, {"e", "n"}},
                                     PrintOptions{false, true, true, false, {"f", "n"}},
                                     PrintOptions{true, true, true, false, {"e", "f", "n"}},
                                     PrintOptions{false, false, false, true, {"t"}}));

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
        std::make_tuple(std::string("1"), PrintOptions{false, false, false, false, {}}),
        std::make_tuple(std::string("1"), PrintOptions{true, false, false, false, {"e"}}),
        std::make_tuple(std::string("1"), PrintOptions{false, true, false, false, {"f"}}),
        std::make_tuple(std::string("1"), PrintOptions{false, false, true, false, {"n"}}),
        std::make_tuple(std::string("1"), PrintOptions{true, true, false, false, {"e", "f"}}),
        std::make_tuple(std::string("1"), PrintOptions{true, false, true, false, {"e", "n"}}),
        std::make_tuple(std::string("1"), PrintOptions{false, true, true, false, {"f", "n"}}),
        std::make_tuple(std::string("1"), PrintOptions{true, true, true, false, {"e", "f", "n"}}),
        std::make_tuple(std::string("1"), PrintOptions{false, false, false, true, {"t"}}),
        std::make_tuple(std::string("2c"), PrintOptions{false, false, false, false, {}}),
        std::make_tuple(std::string("2c"), PrintOptions{true, false, false, false, {"e"}}),
        std::make_tuple(std::string("2c"), PrintOptions{false, true, false, false, {"f"}}),
        std::make_tuple(std::string("2c"), PrintOptions{false, false, true, false, {"n"}}),
        std::make_tuple(std::string("2c"), PrintOptions{true, true, false, false, {"e", "f"}}),
        std::make_tuple(std::string("2c"), PrintOptions{true, false, true, false, {"e", "n"}}),
        std::make_tuple(std::string("2c"), PrintOptions{false, true, true, false, {"f", "n"}}),
        std::make_tuple(std::string("2c"), PrintOptions{true, true, true, false, {"e", "f", "n"}}),
        std::make_tuple(std::string("2c"), PrintOptions{false, false, false, true, {"t"}}),
        std::make_tuple(std::string("3"), PrintOptions{false, false, false, false, {}}),
        std::make_tuple(std::string("3"), PrintOptions{true, false, false, false, {"e"}}),
        std::make_tuple(std::string("3"), PrintOptions{false, true, false, false, {"f"}}),
        std::make_tuple(std::string("3"), PrintOptions{false, false, true, false, {"n"}}),
        std::make_tuple(std::string("3"), PrintOptions{true, true, false, false, {"e", "f"}}),
        std::make_tuple(std::string("3"), PrintOptions{true, false, true, false, {"e", "n"}}),
        std::make_tuple(std::string("3"), PrintOptions{false, true, true, false, {"f", "n"}}),
        std::make_tuple(std::string("3"), PrintOptions{true, true, true, false, {"e", "f", "n"}}),
        std::make_tuple(std::string("3"), PrintOptions{false, false, false, true, {"t"}})));
#endif
