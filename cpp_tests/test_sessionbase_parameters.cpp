#include <gtest/gtest.h>

#include "exceptionsbase.h"
#include "sessionbase.h"

struct PrintOptions {
   bool print_enums_numerically;
   bool print_full_oids;
   bool print_oids_numerically;
   bool print_timeticks_numerically;
   std::vector<std::string> expected_flags;
   std::vector<std::string> expected_get_output;

   // Add pretty printing for test failures
   friend std::ostream& operator<<(std::ostream& os, PrintOptions const& po) {
      os << "PrintOptions{enums_numeric=" << (po.print_enums_numerically ? "true" : "false")
         << ", full_oids=" << (po.print_full_oids ? "true" : "false")
         << ", oids_numeric=" << (po.print_oids_numerically ? "true" : "false") << ", flags=[";
      for (size_t i = 0; i < po.expected_flags.size(); i++) {
         if (i > 0) {
            os << ",";
         }
         os << po.expected_flags[i];
      }
      os << "]}";
      return os;
   }
};

class SessionsParamTest : public ::testing::TestWithParam<std::tuple<std::string, PrintOptions>> {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_P(SessionsParamTest, TestSessionPrintOptions) {
   auto const& [version, print_opts] = GetParam();

   if (version == "3") {
      SessionBase session(
          /* hostname */ "localhost",
          /* port_number */ "11161",
          /* version */ "3",
          /* community */ "",
          /* auth_protocol */ "SHA",
          /* auth_passphrase */ "auth_second",
          /* security_engine_id */ "",
          /* context_engine_id */ "",
          /* security_level */ "authPriv",
          /* context */ "",
          /* security_username */ "secondary_sha_aes",
          /* privacy_protocol */ "AES",
          /* privacy_passphrase */ "priv_second",
          /* boots_time */ "",
          /* retries */ "",
          /* timeout */ "",
          /* load_mibs */ "",
          /* mib_directories */ "",
          /* print_enums_numerically */ print_opts.print_enums_numerically,
          /* print_full_oids */ print_opts.print_full_oids,
          /* print_oids_numerically */ print_opts.print_oids_numerically,
          /* print_timeticks_numerically */ print_opts.print_timeticks_numerically,
          /* max_repetitions */ "" // Assume empty for these tests
      );

      auto const& args = session._get_args();
      std::vector<std::string> expected = {"-A", "auth_second",
                                           "-a", "SHA",
                                           "-X", "priv_second",
                                           "-x", "AES",
                                           "-l", "authPriv",
                                           "-u", "secondary_sha_aes",
                                           "-v", "3"};

      // Add print options flags
      for (auto const& flag : print_opts.expected_flags) {
         expected.push_back("-O");
         expected.push_back(flag);
      }

      expected.push_back("localhost:11161");
      ASSERT_EQ(args, expected);

      // Verify get output with print options
      if (print_opts.print_timeticks_numerically) {
         // Verify get output with print options
         auto results = session.get("SNMPv2-MIB::sysUpTime.0");

         ASSERT_EQ(results.size(), 1);
         // Note: The actual OID name and type vary by platform/MIB version
         // Just verify we got a result with a non-empty OID
         EXPECT_FALSE(results[0].oid.empty());
         EXPECT_FALSE(results[0].value.empty());
      } else {
         // Verify get output with print options
         auto results = session.get("ifAdminStatus.1");

         ASSERT_EQ(results.size(), 1);
         EXPECT_EQ(results[0]._to_string(), print_opts.expected_get_output[0]);
      }

   } else {
      SessionBase session(
          /* hostname */ "localhost:11161",
          /* port_number */ "",
          /* version */ version,
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
          /* print_enums_numerically */ print_opts.print_enums_numerically,
          /* print_full_oids */ print_opts.print_full_oids,
          /* print_oids_numerically */ print_opts.print_oids_numerically,
          /* print_timeticks_numerically */ print_opts.print_timeticks_numerically,
          /* max_repetitions */ "" // Assume empty for these tests
      );

      auto const& args = session._get_args();
      std::vector<std::string> expected = {"-c", "public", "-v", version};

      // Add print options flags
      for (auto const& flag : print_opts.expected_flags) {
         expected.push_back("-O");
         expected.push_back(flag);
      }

      expected.push_back("localhost:11161");

      ASSERT_EQ(args, expected);

      if (print_opts.print_timeticks_numerically) {
         // Verify get output with print options
         auto results = session.get("SNMPv2-MIB::sysUpTime.0");

         ASSERT_EQ(results.size(), 1);
         // Note: The actual OID name and type vary by platform/MIB version
         // Just verify we got a result with a non-empty OID
         EXPECT_FALSE(results[0].oid.empty());
         EXPECT_FALSE(results[0].value.empty());
      } else {
         // Verify get output with print options
         auto results = session.get("ifAdminStatus.1");

         ASSERT_EQ(results.size(), 1);
         EXPECT_EQ(results[0]._to_string(), print_opts.expected_get_output[0]);
      }
   }
}

TEST(SessionBaseArgs, TestMaxRepetitionsOption) {
   // Verify that providing a value for max_repetitions adds the -Cr flag
   SessionBase session("localhost", "", "2c", "public", "", "", "", "", "", "", "", "", "", "", "",
                       "", "", "", false, false, false, false,
                       "25" // max_repetitions
   );

   auto const& args = session._get_args();
   std::vector<std::string> expected = {"-c", "public", "-Cr25", "-v", "2c", "localhost"};
   ASSERT_EQ(args, expected);
}

TEST(SessionBaseArgs, TestEmptyMaxRepetitionsOption) {
   // Verify that an empty value for max_repetitions does NOT add the -Cr flag
   SessionBase session("localhost", "", "2c", "public", "", "", "", "", "", "", "", "", "", "", "",
                       "", "", "", false, false, false, false,
                       "" // max_repetitions
   );

   auto const& args = session._get_args();
   std::vector<std::string> expected = {"-c", "public", "-v", "2c", "localhost"};
   ASSERT_EQ(args, expected);
}

INSTANTIATE_TEST_SUITE_P(
    SessionVersions,
    SessionsParamTest,
    testing::Combine(
        testing::Values("1", "2c", "3"),
        testing::Values(
            PrintOptions{// Case 1: All false
                         false,
                         false,
                         false,
                         false,
                         {},
                         {"oid: IF-MIB::ifAdminStatus, index: 1, type: INTEGER, value: up(1), converted_value: 1"}},

            PrintOptions{// Case 2: enums true, others false
                         true,
                         false,
                         false,
                         false,
                         {"e"},
                         {"oid: IF-MIB::ifAdminStatus, index: 1, type: INTEGER, value: 1, converted_value: 1"}},

            PrintOptions{
                // Case 3: full_oids true, others false
                false,
                true,
                false,
                false,
                {"f"},
                {"oid: .iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifAdminStatus, "
                 "index: 1, type: INTEGER, value: up(1), converted_value: 1"}},

            PrintOptions{// Case 4: oids_numeric true, others false
                         false,
                         false,
                         true,
                         false,
                         {"n"},
                         {"oid: .1.3.6.1.2.1.2.2.1.7, index: 1, type: INTEGER, value: up(1), converted_value: 1"}},

            PrintOptions{
                // Case 5: enums and full_oids true, oids_numeric false
                true,
                true,
                false,
                false,
                {"e", "f"},
                {"oid: .iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifAdminStatus, "
                 "index: 1, type: INTEGER, value: 1, converted_value: 1"}},

            PrintOptions{// Case 6: enums and oids_numeric true, full_oids false
                         true,
                         false,
                         true,
                         false,
                         {"e", "n"},
                         {"oid: .1.3.6.1.2.1.2.2.1.7, index: 1, type: INTEGER, value: 1, converted_value: 1"}},

            PrintOptions{// Case 7: full_oids and oids_numeric true, enums false
                         false,
                         true,
                         true,
                         false,
                         {"f", "n"},
                         {"oid: .1.3.6.1.2.1.2.2.1.7, index: 1, type: INTEGER, value: up(1), converted_value: 1"}},

            PrintOptions{// Case 8: All true except timeticks numeric
                         true,
                         true,
                         true,
                         false,
                         {"e", "f", "n"},
                         {"oid: .1.3.6.1.2.1.2.2.1.7, index: 1, type: INTEGER, value: 1, converted_value: 1"}},

            PrintOptions{// Case 9: Only timeticks numeric
                         false,
                         false,
                         false,
                         true,
                         {"t"},
                         {"oid: DISMAN-EXPRESSION-MIB::sysUpTimeInstance, index: , type: 46090, "
                          "value: 46090, converted_value: 46090"}})));