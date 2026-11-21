#include <gtest/gtest.h>

#include <string>
#include <vector>

#include "exceptionsbase.h"
#include "sessionbase.h"

struct AddressingCase {
   std::string name;
   std::string hostname;
   std::string port_number;
   std::string version;
   std::string community;
   std::string auth_protocol;
   std::string auth_passphrase;
   std::string security_level;
   std::string security_username;
   std::string privacy_protocol;
   std::string privacy_passphrase;
   std::string expected_hostname;
   std::string expected_port;
   std::vector<std::string> expected_args;
};

class SessionBaseAddressingTest : public ::testing::TestWithParam<AddressingCase> {};

TEST_P(SessionBaseAddressingTest, ParsesAddressAndBuildsArgs) {
   AddressingCase const& tc = GetParam();
   SessionBase session(tc.hostname, tc.port_number, tc.version, tc.community, tc.auth_protocol,
                       tc.auth_passphrase, "", "", tc.security_level, "", tc.security_username,
                       tc.privacy_protocol, tc.privacy_passphrase);

   EXPECT_EQ(session._get_hostname(), tc.expected_hostname);
   EXPECT_EQ(session._get_port_number(), tc.expected_port);
   ASSERT_EQ(session._get_args(), tc.expected_args);
}

INSTANTIATE_TEST_SUITE_P(
    AddressingVariants,
    SessionBaseAddressingTest,
    ::testing::Values(
        AddressingCase{"IPv6AddressWithPort", "[2001:db8::]:162", "", "1", "public", "", "", "", "",
                       "", "", "[2001:db8::]", "162",
                       std::vector<std::string>{"-c", "public", "-r", "3", "-t", "1", "-v", "1",
                                                "[2001:db8::]:162"}},
        AddressingCase{"UDP6Address", "udp6:[2001:db8::]", "161", "1", "public", "", "", "", "", "",
                       "", "udp6:[2001:db8::]", "161",
                       std::vector<std::string>{"-c", "public", "-r", "3", "-t", "1", "-v", "1",
                                                "udp6:[2001:db8::]:161"}},
        AddressingCase{"UDP6AddressWithPort", "udp6:[2001:db8::]:161", "", "1", "public", "", "",
                       "", "", "", "", "udp6:[2001:db8::]", "161",
                       std::vector<std::string>{"-c", "public", "-r", "3", "-t", "1", "-v", "1",
                                                "udp6:[2001:db8::]:161"}},
        AddressingCase{"BasicV1Session", "localhost", "161", "1", "public", "", "", "", "", "", "",
                       "localhost", "161",
                       std::vector<std::string>{"-c", "public", "-r", "3", "-t", "1", "-v", "1",
                                                "localhost:161"}},
        AddressingCase{"V3Session", "localhost", "161", "3", "", "SHA", "auth_pass", "authPriv",
                       "username", "AES", "priv_pass", "localhost", "161",
                       std::vector<std::string>{"-A", "auth_pass", "-a", "SHA", "-X", "priv_pass",
                                                "-x", "AES", "-r", "3", "-l", "authPriv", "-u",
                                                "username", "-t", "1", "-v", "3", "localhost:161"}},
        AddressingCase{"HostnameWithPortV1", "localhost:162", "", "1", "public", "", "", "", "", "",
                       "", "localhost", "162",
                       std::vector<std::string>{"-c", "public", "-r", "3", "-t", "1", "-v", "1",
                                                "localhost:162"}},
        AddressingCase{"HostnameWithPortV2c", "localhost:162", "", "2c", "public", "", "", "", "",
                       "", "", "localhost", "162",
                       std::vector<std::string>{"-c", "public", "-r", "3", "-t", "1", "-v", "2c",
                                                "localhost:162"}},
        AddressingCase{"HostnameWithPortV3", "localhost:162", "", "3", "", "SHA", "auth_pass",
                       "authPriv", "username", "AES", "priv_pass", "localhost", "162",
                       std::vector<std::string>{"-A", "auth_pass", "-a", "SHA", "-X", "priv_pass",
                                                "-x", "AES", "-r", "3", "-l", "authPriv", "-u",
                                                "username", "-t", "1", "-v", "3", "localhost:162"}},
        AddressingCase{"IPv6WithUdp6V1", "udp6:[2001:db8::]", "", "1", "public", "", "", "", "", "",
                       "", "udp6:[2001:db8::]", "",
                       std::vector<std::string>{"-c", "public", "-r", "3", "-t", "1", "-v", "1",
                                                "udp6:[2001:db8::]"}},
        AddressingCase{"IPv6WithUdp6V2c", "udp6:[2001:db8::]", "", "2c", "public", "", "", "", "",
                       "", "", "udp6:[2001:db8::]", "",
                       std::vector<std::string>{"-c", "public", "-r", "3", "-t", "1", "-v", "2c",
                                                "udp6:[2001:db8::]"}},
        AddressingCase{
            "IPv6WithUdp6V3", "udp6:[2001:db8::]", "", "3", "", "SHA", "auth_pass", "authPriv",
            "username", "AES", "priv_pass", "udp6:[2001:db8::]", "",
            std::vector<std::string>{"-A", "auth_pass", "-a", "SHA", "-X", "priv_pass", "-x", "AES",
                                     "-r", "3", "-l", "authPriv", "-u", "username", "-t", "1", "-v",
                                     "3", "udp6:[2001:db8::]"}},
        AddressingCase{
            "EmptyHostname", "", "161", "1", "public", "", "", "", "", "", "", "", "161",
            std::vector<std::string>{"-c", "public", "-r", "3", "-t", "1", "-v", "1", ""}},
        AddressingCase{"IPv6WithoutBrackets", "2001:db8::1", "", "1", "public", "", "", "", "", "",
                       "", "2001:db8::1", "",
                       std::vector<std::string>{"-c", "public", "-r", "3", "-t", "1", "-v", "1",
                                                "2001:db8::1"}}),
    [](testing::TestParamInfo<AddressingCase> const& info) { return info.param.name; });

struct InvalidAddressingCase {
   std::string name;
   std::string hostname;
   std::string port_number;
};

class SessionBaseInvalidAddressingTest : public ::testing::TestWithParam<InvalidAddressingCase> {};

TEST_P(SessionBaseInvalidAddressingTest, ThrowsParseErrorWhenPortProvidedTwice) {
   InvalidAddressingCase const& tc = GetParam();
   EXPECT_THROW(SessionBase(tc.hostname, tc.port_number, "1", "public"), ParseErrorBase);
}

INSTANTIATE_TEST_SUITE_P(
    InvalidAddressingVariants,
    SessionBaseInvalidAddressingTest,
    ::testing::Values(InvalidAddressingCase{"HostnameWithEmbeddedPort", "localhost:162", "161"},
                      InvalidAddressingCase{"UDP6WithEmbeddedPort", "udp6:[2001:db8::]:162", "161"},
                      InvalidAddressingCase{"BracketedIPv6WithEmbeddedPort", "[2001:db8::]:162",
                                            "161"}),
    [](testing::TestParamInfo<InvalidAddressingCase> const& info) { return info.param.name; });
