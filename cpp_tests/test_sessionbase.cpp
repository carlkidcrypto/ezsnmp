#include <gtest/gtest.h>

#include "exceptionsbase.h"
#include "sessionbase.h"

class SessionBaseTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SessionBaseTest, TestBasicV1Session) {
   SessionBase session(
       /* hostname */ "localhost",
       /* port_number */ "161",
       /* version */ "1",
       /* community */ "public");
   auto args = session._get_args();
   std::vector<std::string> expected = {"-c", "public", "-r",           "3", "-t", "1",
                                        "-v", "1",      "localhost:161"};
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestV3Session) {
   SessionBase session(
       /* hostname */ "localhost",
       /* port_number */ "161",
       /* version */ "3",
       /* community */ "",
       /* auth_protocol */ "SHA",
       /* auth_passphrase */ "auth_pass",
       /* security_engine_id */ "",
       /* context_engine_id */ "",
       /* security_level */ "authPriv",
       /* context */ "",
       /* security_username */ "username",
       /* privacy_protocol */ "AES",
       /* privacy_passphrase */ "priv_pass");
   auto args = session._get_args();
   std::vector<std::string> expected = {
       "-A", "auth_pass", "-a", "SHA",      "-X", "priv_pass", "-x", "AES", "-r",           "3",
       "-l", "authPriv",  "-u", "username", "-t", "1",         "-v", "3",   "localhost:161"};
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestHostnameWithPortV1) {
   SessionBase session(
       /* hostname */ "localhost:162",
       /* port_number */ "",
       /* version */ "1",
       /* community */ "public");
   auto args = session._get_args();
   std::vector<std::string> expected = {"-c", "public", "-r",           "3", "-t", "1",
                                        "-v", "1",      "localhost:162"};
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestHostnameWithPortV2c) {
   SessionBase session(
       /* hostname */ "localhost:162",
       /* port_number */ "",
       /* version */ "2c",
       /* community */ "public");
   auto args = session._get_args();
   std::vector<std::string> expected = {"-c", "public", "-r",           "3", "-t", "1",
                                        "-v", "2c",     "localhost:162"};
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestHostnameWithPortV3) {
   SessionBase session(
       /* hostname */ "localhost:162",
       /* port_number */ "",
       /* version */ "3",
       /* community */ "",
       /* auth_protocol */ "SHA",
       /* auth_passphrase */ "auth_pass",
       /* security_engine_id */ "",
       /* context_engine_id */ "",
       /* security_level */ "authPriv",
       /* context */ "",
       /* security_username */ "username",
       /* privacy_protocol */ "AES",
       /* privacy_passphrase */ "priv_pass");
   auto args = session._get_args();
   std::vector<std::string> expected = {
       "-A", "auth_pass", "-a", "SHA",      "-X", "priv_pass", "-x", "AES", "-r",           "3",
       "-l", "authPriv",  "-u", "username", "-t", "1",         "-v", "3",   "localhost:162"};
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestIPv6WithUdp6) {
   SessionBase session(
       /* hostname */ "udp6:[2001:db8::]",
       /* port_number */ "",
       /* version */ "1",
       /* community */ "public");
   auto args = session._get_args();
   std::vector<std::string> expected = {"-c", "public",           "-r", "3", "-t", "1", "-v",
                                        "1",  "udp6:[2001:db8::]"};
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestIPv6WithUdp6V2c) {
   SessionBase session(
       /* hostname */ "udp6:[2001:db8::]",
       /* port_number */ "",
       /* version */ "2c",
       /* community */ "public");
   auto args = session._get_args();
   std::vector<std::string> expected = {"-c", "public",           "-r", "3", "-t", "1", "-v",
                                        "2c", "udp6:[2001:db8::]"};
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestIPv6WithUdp6V3) {
   SessionBase session(
       /* hostname */ "udp6:[2001:db8::]",
       /* port_number */ "",
       /* version */ "3",
       /* community */ "",
       /* auth_protocol */ "SHA",
       /* auth_passphrase */ "auth_pass",
       /* security_engine_id */ "",
       /* context_engine_id */ "",
       /* security_level */ "authPriv",
       /* context */ "",
       /* security_username */ "username",
       /* privacy_protocol */ "AES",
       /* privacy_passphrase */ "priv_pass");
   auto args = session._get_args();
   std::vector<std::string> expected = {"-A",
                                        "auth_pass",
                                        "-a",
                                        "SHA",
                                        "-X",
                                        "priv_pass",
                                        "-x",
                                        "AES",
                                        "-r",
                                        "3",
                                        "-l",
                                        "authPriv",
                                        "-u",
                                        "username",
                                        "-t",
                                        "1",
                                        "-v",
                                        "3",
                                        "udp6:[2001:db8::]"};
   ASSERT_EQ(args, expected);
}

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
       /* timeout */ "10");

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

   // Verify final args construction
   auto args = session._get_args();
   std::vector<std::string> expected = {"-A",         "new_auth_pass",
                                        "-a",         "SHA",
                                        "-Z",         "2,3",
                                        "-c",         "private",
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
