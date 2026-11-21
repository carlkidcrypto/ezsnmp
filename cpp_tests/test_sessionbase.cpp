#include <gtest/gtest.h>

#include <algorithm>
#include <iterator>
#include <string>
#include <vector>

#include "exceptionsbase.h"
#include "sessionbase.h"

class SessionBaseTest : public ::testing::Test {};

TEST_F(SessionBaseTest, TestGetters) {
   SessionBase session(
       /* hostname */ "localhost",
       /* port_number */ "161",
       /* version */ "3",
       /* community */ "public",
       /* auth_protocol */ "SHA",
       /* auth_passphrase */ "auth_pass",
       /* security_engine_id */ "8000000001020304",
       /* context_engine_id */ "8000000001020305",
       /* security_level */ "authPriv",
       /* context */ "context1",
       /* security_username */ "username",
       /* privacy_protocol */ "AES",
       /* privacy_passphrase */ "priv_pass",
       /* boots_time */ "1,2",
       /* retries */ "5",
       /* timeout */ "10",
       /* load_mibs */ "ALL",
       /* mib_directories */ "/usr/share/snmp/mibs",
       /* print_enums_numerically */ true,
       /* print_full_oids */ true,
       /* print_oids_numerically */ true,
       /* print_timeticks_numerically */ true,
       /* print_hex_strings */ false,
       /* set_max_repeaters_to_num */ "25");

   EXPECT_EQ(session._get_hostname(), "localhost");
   EXPECT_EQ(session._get_port_number(), "161");
   EXPECT_EQ(session._get_version(), "3");
   EXPECT_EQ(session._get_community(), "public");
   EXPECT_EQ(session._get_auth_protocol(), "SHA");
   EXPECT_EQ(session._get_auth_passphrase(), "auth_pass");
   EXPECT_EQ(session._get_security_engine_id(), "8000000001020304");
   EXPECT_EQ(session._get_context_engine_id(), "8000000001020305");
   EXPECT_EQ(session._get_security_level(), "authPriv");
   EXPECT_EQ(session._get_context(), "context1");
   EXPECT_EQ(session._get_security_username(), "username");
   EXPECT_EQ(session._get_privacy_protocol(), "AES");
   EXPECT_EQ(session._get_privacy_passphrase(), "priv_pass");
   EXPECT_EQ(session._get_boots_time(), "1,2");
   EXPECT_EQ(session._get_retries(), "5");
   EXPECT_EQ(session._get_timeout(), "10");
   EXPECT_EQ(session._get_load_mibs(), "ALL");
   EXPECT_EQ(session._get_mib_directories(), "/usr/share/snmp/mibs");
   EXPECT_TRUE(session._get_print_enums_numerically());
   EXPECT_TRUE(session._get_print_full_oids());
   EXPECT_TRUE(session._get_print_oids_numerically());
   EXPECT_TRUE(session._get_print_timeticks_numerically());
   EXPECT_EQ(session._get_set_max_repeaters_to_num(), "25");
}

TEST_F(SessionBaseTest, TestSetters) {
   SessionBase session(
       /* hostname */ "localhost",
       /* port_number */ "161",
       /* version */ "1",
       /* community */ "public");

   session._set_hostname("newhost");
   EXPECT_EQ(session._get_hostname(), "newhost");

   session._set_port_number("162");
   EXPECT_EQ(session._get_port_number(), "162");

   session._set_version("2c");
   EXPECT_EQ(session._get_version(), "2c");

   session._set_community("private");
   EXPECT_EQ(session._get_community(), "private");

   session._set_boots_time("2,3");
   EXPECT_EQ(session._get_boots_time(), "2,3");

   session._set_retries("4");
   EXPECT_EQ(session._get_retries(), "4");

   session._set_timeout("5");
   EXPECT_EQ(session._get_timeout(), "5");

   session._set_version("3");
   session._set_auth_protocol("SHA");
   EXPECT_EQ(session._get_auth_protocol(), "SHA");

   session._set_auth_passphrase("new_auth_pass");
   EXPECT_EQ(session._get_auth_passphrase(), "new_auth_pass");

   session._set_security_engine_id("8000000001020306");
   EXPECT_EQ(session._get_security_engine_id(), "8000000001020306");

   session._set_context_engine_id("8000000001020307");
   EXPECT_EQ(session._get_context_engine_id(), "8000000001020307");

   session._set_security_level("authPriv");
   EXPECT_EQ(session._get_security_level(), "authPriv");

   session._set_context("newcontext");
   EXPECT_EQ(session._get_context(), "newcontext");

   session._set_security_username("newuser");
   EXPECT_EQ(session._get_security_username(), "newuser");

   session._set_privacy_protocol("DES");
   EXPECT_EQ(session._get_privacy_protocol(), "DES");

   session._set_privacy_passphrase("new_priv_pass");
   EXPECT_EQ(session._get_privacy_passphrase(), "new_priv_pass");

   // When version is "3", community string (-c) should NOT be included
   auto args = session._get_args();
   std::vector<std::string> expected = {"-A",         "new_auth_pass",
                                        "-a",         "SHA",
                                        "-Z",         "2,3",
                                        "-n",         "newcontext",
                                        "-E",         "8000000001020307",
                                        "-X",         "new_priv_pass",
                                        "-x",         "DES",
                                        "-r",         "4",
                                        "-e",         "8000000001020306",
                                        "-l",         "authPriv",
                                        "-u",         "newuser",
                                        "-t",         "5",
                                        "-v",         "3",
                                        "newhost:162"};
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestAllV3Parameters) {
   SessionBase session(
       /* hostname */ "localhost",
       /* port_number */ "161",
       /* version */ "3",
       /* community */ "",
       /* auth_protocol */ "SHA",
       /* auth_passphrase */ "authpass",
       /* security_engine_id */ "80000001",
       /* context_engine_id */ "80000002",
       /* security_level */ "authPriv",
       /* context */ "mycontext",
       /* security_username */ "myuser",
       /* privacy_protocol */ "AES",
       /* privacy_passphrase */ "privpass",
       /* boots_time */ "1,2",
       /* retries */ "5",
       /* timeout */ "10",
       /* load_mibs */ "ALL",
       /* mib_directories */ "/usr/share/snmp/mibs");

   auto args = session._get_args();

   auto hasArgPair = [&args](std::string const& flag, std::string const& value) -> bool {
      auto it = std::find(args.begin(), args.end(), flag);
      if (it != args.end() && std::next(it) != args.end()) {
         return *std::next(it) == value;
      }
      return false;
   };

   EXPECT_TRUE(hasArgPair("-A", "authpass")) << "Auth passphrase not found";
   EXPECT_TRUE(hasArgPair("-a", "SHA")) << "Auth protocol not found";
   EXPECT_TRUE(hasArgPair("-Z", "1,2")) << "Boots time not found";
   EXPECT_TRUE(hasArgPair("-n", "mycontext")) << "Context not found";
   EXPECT_TRUE(hasArgPair("-E", "80000002")) << "Context engine ID not found";
   EXPECT_TRUE(hasArgPair("-m", "ALL")) << "Load MIBs not found";
   EXPECT_TRUE(hasArgPair("-M", "/usr/share/snmp/mibs")) << "MIB directories not found";
   EXPECT_TRUE(hasArgPair("-X", "privpass")) << "Privacy passphrase not found";
   EXPECT_TRUE(hasArgPair("-x", "AES")) << "Privacy protocol not found";
   EXPECT_TRUE(hasArgPair("-r", "5")) << "Retries not found";
   EXPECT_TRUE(hasArgPair("-e", "80000001")) << "Security engine ID not found";
   EXPECT_TRUE(hasArgPair("-l", "authPriv")) << "Security level not found";
   EXPECT_TRUE(hasArgPair("-u", "myuser")) << "Security username not found";
   EXPECT_TRUE(hasArgPair("-t", "10")) << "Timeout not found";
   EXPECT_TRUE(hasArgPair("-v", "3")) << "Version not found";

   ASSERT_FALSE(args.empty());
   EXPECT_EQ(args.back(), "localhost:161") << "Hostname should be the last argument";

   size_t const expected_arg_count = 15 * 2 + 1;
   EXPECT_EQ(args.size(), expected_arg_count) << "Unexpected number of arguments";
}

TEST_F(SessionBaseTest, TestV3WithCommunityIgnored) {
   SessionBase session(
       /* hostname */ "localhost",
       /* port_number */ "161",
       /* version */ "3",
       /* community */ "public",
       /* auth_protocol */ "SHA",
       /* auth_passphrase */ "authpass",
       /* security_engine_id */ "",
       /* context_engine_id */ "",
       /* security_level */ "authPriv",
       /* context */ "",
       /* security_username */ "myuser",
       /* privacy_protocol */ "AES",
       /* privacy_passphrase */ "privpass");

   auto args = session._get_args();
   EXPECT_EQ(std::find(args.begin(), args.end(), "-c"), args.end());
}

TEST_F(SessionBaseTest, TestV3SettersWorkWithoutThrow) {
   SessionBase session("localhost", "161", "3", "", "SHA", "authpass", "", "engine123", "authPriv",
                       "", "testuser", "AES", "privpass");
   session._set_auth_protocol("MD5");
   EXPECT_EQ(session._get_auth_protocol(), "MD5");

   session._set_auth_passphrase("new_pass");
   EXPECT_EQ(session._get_auth_passphrase(), "new_pass");

   session._set_privacy_protocol("DES");
   EXPECT_EQ(session._get_privacy_protocol(), "DES");

   session._set_security_username("newuser");
   EXPECT_EQ(session._get_security_username(), "newuser");
}

// Regression test for GitHub issue #656:
// Calling _get_context() (and other getters) on a default-constructed SessionBase
// must not crash.
TEST_F(SessionBaseTest, TestDefaultConstructedGettersDoNotCrash) {
   SessionBase session;

   EXPECT_EQ(session._get_hostname(), "localhost");
   EXPECT_EQ(session._get_port_number(), "");
   EXPECT_EQ(session._get_version(), "3");
   EXPECT_EQ(session._get_community(), "public");
   EXPECT_EQ(session._get_auth_protocol(), "");
   EXPECT_EQ(session._get_auth_passphrase(), "");
   EXPECT_EQ(session._get_security_engine_id(), "");
   EXPECT_EQ(session._get_context_engine_id(), "");
   EXPECT_EQ(session._get_security_level(), "");
   EXPECT_EQ(session._get_context(), "");
   EXPECT_EQ(session._get_security_username(), "");
   EXPECT_EQ(session._get_privacy_protocol(), "");
   EXPECT_EQ(session._get_privacy_passphrase(), "");
   EXPECT_EQ(session._get_boots_time(), "");
   EXPECT_EQ(session._get_retries(), "3");
   EXPECT_EQ(session._get_timeout(), "1");
   EXPECT_EQ(session._get_load_mibs(), "");
   EXPECT_EQ(session._get_mib_directories(), "");
   EXPECT_FALSE(session._get_print_enums_numerically());
   EXPECT_FALSE(session._get_print_full_oids());
   EXPECT_FALSE(session._get_print_oids_numerically());
   EXPECT_FALSE(session._get_print_timeticks_numerically());
   EXPECT_EQ(session._get_set_max_repeaters_to_num(), "");

   auto args = session._get_args();
   EXPECT_FALSE(args.empty());
   EXPECT_NE(std::find(args.begin(), args.end(), "-v"), args.end());
   EXPECT_EQ(args.back(), "localhost");
}

TEST_F(SessionBaseTest, TestCloseSession) {
   SessionBase session("localhost", "161", "2c", "public");
   EXPECT_NO_THROW(session._close());
}

TEST_F(SessionBaseTest, TestCloseMethod) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "1", "1");
   EXPECT_NO_THROW(session._close());
}
