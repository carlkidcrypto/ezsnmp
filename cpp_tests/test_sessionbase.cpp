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

TEST_F(SessionBaseTest, TestHostnameWithPort) {
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

TEST_F(SessionBaseTest, TestPrintOptions) {
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
       /* print_oids_numerically */ true);
   auto args = session._get_args();
   std::vector<std::string> expected = {"-c", "public", "-v", "1", "-O",           "e",
                                        "-O", "f",      "-O", "n", "localhost:161"};
   ASSERT_EQ(args, expected);
}
