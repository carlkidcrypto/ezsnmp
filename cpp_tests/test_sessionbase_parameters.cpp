#include <gtest/gtest.h>

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
   std::vector<std::string> args = {"-c", "public", "-r", "3", "-t", "1", "-v", version};
   for (auto const& flag : options.expected_flags) {
      args.push_back("-O");
      args.push_back(flag);
   }
   args.push_back("localhost:161");
   return args;
}

TEST_P(SessionsParamTest, PrintOptionsAreAppliedToArgs) {
   auto const& [version, options] = GetParam();

   SessionBase session("localhost",
                       "161",
                       version,
                       "public",
                       "",
                       "",
                       "",
                       "",
                       "",
                       "",
                       "",
                       "",
                       "",
                       "",
                       "",
                       "",
                       "",
                       "",
                       options.print_enums_numerically,
                       options.print_full_oids,
                       options.print_oids_numerically,
                       options.print_timeticks_numerically);

   auto args = session._get_args();
   auto expected = build_expected_args(version, options);
   EXPECT_EQ(args, expected);
}

static const auto SESSION_PARAM_VALUES = testing::Combine(
    testing::Values(std::string("1"), std::string("2c"), std::string("3")),
    testing::Values(
        PrintOptions{false, false, false, false, {}},
        PrintOptions{true, false, false, false, {"e"}},
        PrintOptions{false, true, false, false, {"f"}},
        PrintOptions{false, false, true, false, {"n"}},
        PrintOptions{true, true, false, false, {"e", "f"}},
        PrintOptions{true, false, true, false, {"e", "n"}},
        PrintOptions{false, true, true, false, {"f", "n"}},
        PrintOptions{true, true, true, false, {"e", "f", "n"}},
        PrintOptions{false, false, false, true, {"t"}}));

#if defined(INSTANTIATE_TEST_SUITE_P)
INSTANTIATE_TEST_SUITE_P(
    SessionVersions,
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
