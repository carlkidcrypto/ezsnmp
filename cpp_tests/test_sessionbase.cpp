#include <gtest/gtest.h>
#include "exceptionsbase.h"
#include "sessionbase.h"

class SessionBaseTest : public ::testing::Test {
protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SessionBaseTest, TestBasicV1Session) {
   SessionBase session("localhost", "161", "1", "public");
   auto args = session._get_args();
   
   std::vector<std::string> expected = {
      "-c", "public",
      "-v", "1",
      "localhost:161"
   };
   
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestV3Session) {
   SessionBase session("localhost", "161", "3", "", "SHA", "auth_pass", 
      "", "", "authPriv", "", "username", "AES", "priv_pass");
   
   auto args = session._get_args();
   std::vector<std::string> expected = {
      "-v", "3",
      "-a", "SHA",
      "-A", "auth_pass", 
      "-l", "authPriv",
      "-u", "username",
      "-x", "AES",
      "-X", "priv_pass",
      "localhost:161"
   };
   
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestHostnameWithPort) {
   SessionBase session("localhost:162", "", "1", "public");
   
   EXPECT_EQ(session._get_hostname(), "localhost");
   EXPECT_EQ(session._get_port_number(), "162");
   
   auto args = session._get_args();
   std::vector<std::string> expected = {
      "-c", "public",
      "-v", "1", 
      "localhost:162"
   };
   
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestIPv6Address) {
   SessionBase session("[2001:db8::]", "161", "1", "public");
   
   EXPECT_EQ(session._get_hostname(), "[2001:db8::]");
   EXPECT_EQ(session._get_port_number(), "161");
   
   auto args = session._get_args();
   std::vector<std::string> expected = {
      "-c", "public",
      "-v", "1",
      "[2001:db8::]:161" 
   };
   
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestIPv6AddressWithPort) {
   SessionBase session("[2001:db8::]:162", "", "1", "public");
   
   EXPECT_EQ(session._get_hostname(), "[2001:db8::]");
   EXPECT_EQ(session._get_port_number(), "162");
   
   auto args = session._get_args();
   std::vector<std::string> expected = {
      "-c", "public", 
      "-v", "1",
      "[2001:db8::]:162"
   };
   
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestUDP6Address) {
   SessionBase session("udp6:[2001:db8::]", "161", "1", "public");
   
   EXPECT_EQ(session._get_hostname(), "udp6:[2001:db8::]");
   EXPECT_EQ(session._get_port_number(), "161");
   
   auto args = session._get_args();
   std::vector<std::string> expected = {
      "-c", "public",
      "-v", "1", 
      "udp6:[2001:db8::]:161"
   };
   
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestPrintOptions) {
   SessionBase session("localhost", "161", "1", "public", "", "", "", "", "", "", "", "", "",
      "", "", "", "", "", true, true, true);
      
   auto args = session._get_args();
   std::vector<std::string> expected = {
      "-c", "public",
      "-v", "1",
      "-O", "efn", 
      "localhost:161"
   };
   
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestInvalidHostnamePortCombination) {
   EXPECT_THROW(
      SessionBase("localhost:162", "161", "1", "public"),
      ParseErrorBase
   );
}