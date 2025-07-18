#include <gtest/gtest.h>

#include "exceptionsbase.h"
#include "sessionbase.h"

class SessionBaseTest : public ::testing::Test {
  protected:
   void SetUp() override {}
   void TearDown() override {}
};

TEST_F(SessionBaseTest, TestIPv6AddressWithPort) {
   SessionBase session("[2001:db8::]:162", "", "1", "public");

   EXPECT_EQ(session._get_hostname(), "[2001:db8::]");
   EXPECT_EQ(session._get_port_number(), "162");

   auto args = session._get_args();
   std::vector<std::string> expected = {"-c", "public",          "-r", "3", "-t", "1", "-v",
                                        "1",  "[2001:db8::]:162"};

   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestUDP6Address) {
   SessionBase session("udp6:[2001:db8::]", "161", "1", "public");

   EXPECT_EQ(session._get_hostname(), "udp6:[2001:db8::]");
   EXPECT_EQ(session._get_port_number(), "161");

   auto args = session._get_args();
   std::vector<std::string> expected = {
       "-c", "public", "-r", "3", "-t", "1", "-v", "1", "udp6:[2001:db8::]:161"};

   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestUDP6AddressWithPort) {
   // Test an IPv6 address with udp6 prefix and port number after closing bracket
   SessionBase session("udp6:[2001:db8::]:161", "", "1", "public");

   // Verify hostname extraction (should include udp6: prefix and brackets)
   EXPECT_EQ(session._get_hostname(), "udp6:[2001:db8::]");

   // Verify port number extraction from after the closing bracket
   EXPECT_EQ(session._get_port_number(), "161");

   // Verify complete args construction
   auto args = session._get_args();
   std::vector<std::string> expected = {
       "-c", "public", "-r", "3", "-t", "1", "-v", "1", "udp6:[2001:db8::]:161"};

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
       /* print_oids_numerically */ true,
       /* print_timeticks_numerically */ true);
   auto args = session._get_args();
   std::vector<std::string> expected = {"-c", "public", "-v", "1", "-O",           "e", "-O", "f",
                                        "-O", "n",      "-O", "t", "localhost:161"};
   ASSERT_EQ(args, expected);
}

TEST_F(SessionBaseTest, TestInvalidHostnamePortCombination) {
   EXPECT_THROW(SessionBase("localhost:162", "161", "1", "public"), ParseErrorBase);
}

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

TEST_F(SessionBaseTest, TestWalkSingleMib) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");
   auto result = session.walk("SNMPv2-MIB::sysORDescr");

#ifdef __APPLE__
   EXPECT_EQ(result[0]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 1, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(result[1]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 2, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(result[2]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 3, type: STRING, value: The SNMP Management "
             "Architecture MIB.");
   EXPECT_EQ(result[3]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 4, type: STRING, value: The MIB modules for "
             "managing SNMP Notification, plus filtering.");
   EXPECT_EQ(result[4]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 5, type: STRING, value: The MIB module for "
             "logging SNMP Notifications.");
#else
   EXPECT_EQ(result[0]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 1, type: STRING, value: The SNMP Management "
             "Architecture MIB.");
   EXPECT_EQ(result[1]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 2, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(result[2]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 3, type: STRING, value: The management "
             "information definitions for the SNMP User-based Security Model.");
   EXPECT_EQ(result[3]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 4, type: STRING, value: The MIB module for "
             "SNMPv2 entities");
   EXPECT_EQ(result[4]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 5, type: STRING, value: View-based Access "
             "Control Model for SNMP.");
   EXPECT_EQ(result[5]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 6, type: STRING, value: The MIB module for "
             "managing TCP implementations");
   EXPECT_EQ(result[6]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 7, type: STRING, value: The MIB module for "
             "managing UDP implementations");
   EXPECT_EQ(result[7]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 8, type: STRING, value: The MIB module for "
             "managing IP and ICMP implementations");
   EXPECT_EQ(result[8]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 9, type: STRING, value: The MIB modules for "
             "managing SNMP Notification, plus filtering.");
   EXPECT_EQ(result[9]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 10, type: STRING, value: The MIB module for "
             "logging SNMP Notifications.");
#endif
}

TEST_F(SessionBaseTest, TestBulkWalkSingleMib) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");
   auto result = session.bulk_walk("SNMPv2-MIB::sysORDescr");

#ifdef __APPLE__
   EXPECT_EQ(result[0]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 1, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(result[1]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 2, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(result[2]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 3, type: STRING, value: The SNMP Management "
             "Architecture MIB.");
   EXPECT_EQ(result[3]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 4, type: STRING, value: The MIB modules for "
             "managing SNMP Notification, plus filtering.");
   EXPECT_EQ(result[4]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 5, type: STRING, value: The MIB module for "
             "logging SNMP Notifications.");
#else
   EXPECT_EQ(result[0]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 1, type: STRING, value: The SNMP Management "
             "Architecture MIB.");
   EXPECT_EQ(result[1]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 2, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(result[2]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 3, type: STRING, value: The management "
             "information definitions for the SNMP User-based Security Model.");
   EXPECT_EQ(result[3]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 4, type: STRING, value: The MIB module for "
             "SNMPv2 entities");
   EXPECT_EQ(result[4]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 5, type: STRING, value: View-based Access "
             "Control Model for SNMP.");
   EXPECT_EQ(result[5]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 6, type: STRING, value: The MIB module for "
             "managing TCP implementations");
   EXPECT_EQ(result[6]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 7, type: STRING, value: The MIB module for "
             "managing UDP implementations");
   EXPECT_EQ(result[7]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 8, type: STRING, value: The MIB module for "
             "managing IP and ICMP implementations");
   EXPECT_EQ(result[8]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 9, type: STRING, value: The MIB modules for "
             "managing SNMP Notification, plus filtering.");
   EXPECT_EQ(result[9]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 10, type: STRING, value: The MIB module for "
             "logging SNMP Notifications.");
#endif
}

// BROKEN< THERE"S A BUG HERE. bulkwalk only walks one OID.
// TEST_F(SessionBaseTest, TestBulkWalkMultipleMibs) {
//     SessionBase session(
//         "localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "", "3", "5");
//     std::vector<std::string> mibs = {
//         "sysORDescr",
//         "sysORID"
//     };
//     auto result = session.bulk_walk(mibs);
//     ASSERT_FALSE(result.empty());

//     // Check sysORDescr entries
//     EXPECT_EQ(result[0]._to_string(), "oid: SNMPv2-MIB::sysORDescr, index: 1, type: STRING,
//     value: The SNMP Management Architecture MIB."); EXPECT_EQ(result[1]._to_string(), "oid:
//     SNMPv2-MIB::sysORDescr, index: 2, type: STRING, value: The MIB for Message Processing and
//     Dispatching."); EXPECT_EQ(result[2]._to_string(), "oid: SNMPv2-MIB::sysORDescr, index: 3,
//     type: STRING, value: The management information definitions for the SNMP User-based Security
//     Model."); EXPECT_EQ(result[3]._to_string(), "oid: SNMPv2-MIB::sysORDescr, index: 4, type:
//     STRING, value: The MIB module for SNMPv2 entities"); EXPECT_EQ(result[4]._to_string(), "oid:
//     SNMPv2-MIB::sysORDescr, index: 5, type: STRING, value: View-based Access Control Model for
//     SNMP."); EXPECT_EQ(result[5]._to_string(), "oid: SNMPv2-MIB::sysORDescr, index: 6, type:
//     STRING, value: The MIB module for managing TCP implementations");
//     EXPECT_EQ(result[6]._to_string(), "oid: SNMPv2-MIB::sysORDescr, index: 7, type: STRING,
//     value: The MIB module for managing UDP implementations"); EXPECT_EQ(result[7]._to_string(),
//     "oid: SNMPv2-MIB::sysORDescr, index: 8, type: STRING, value: The MIB module for managing IP
//     and ICMP implementations"); EXPECT_EQ(result[8]._to_string(), "oid: SNMPv2-MIB::sysORDescr,
//     index: 9, type: STRING, value: The MIB modules for managing SNMP Notification, plus
//     filtering."); EXPECT_EQ(result[9]._to_string(), "oid: SNMPv2-MIB::sysORDescr, index: 10,
//     type: STRING, value: The MIB module for logging SNMP Notifications.");

//     // Check sysORID entries
//     EXPECT_EQ(result[10]._to_string(), "oid: SNMPv2-MIB::sysORID, index: 1, type: OBJID, value:
//     SNMPv2-SMI::mib-2.49.1"); EXPECT_EQ(result[11]._to_string(), "oid: SNMPv2-MIB::sysORID,
//     index: 2, type: OBJID, value: SNMP-MPD-MIB::snmpMPDMIB"); EXPECT_EQ(result[12]._to_string(),
//     "oid: SNMPv2-MIB::sysORID, index: 3, type: OBJID, value: SNMP-USER-BASED-SM-MIB::usmMIB");
//     EXPECT_EQ(result[13]._to_string(), "oid: SNMPv2-MIB::sysORID, index: 4, type: OBJID, value:
//     SNMPv2-MIB::snmpMIB"); EXPECT_EQ(result[14]._to_string(), "oid: SNMPv2-MIB::sysORID, index:
//     5, type: OBJID, value: SNMP-VIEW-BASED-ACM-MIB::vacmBasicGroup");
//     EXPECT_EQ(result[15]._to_string(), "oid: SNMPv2-MIB::sysORID, index: 6, type: OBJID, value:
//     TCP-MIB::tcpMIB"); EXPECT_EQ(result[16]._to_string(), "oid: SNMPv2-MIB::sysORID, index: 7,
//     type: OBJID, value: UDP-MIB::udpMIB"); EXPECT_EQ(result[17]._to_string(), "oid:
//     SNMPv2-MIB::sysORID, index: 8, type: OBJID, value: IP-MIB::ip");
//     EXPECT_EQ(result[18]._to_string(), "oid: SNMPv2-MIB::sysORID, index: 9, type: OBJID, value:
//     SNMP-NOTIFICATION-MIB::snmpNotificationMIB"); EXPECT_EQ(result[19]._to_string(), "oid:
//     SNMPv2-MIB::sysORID, index: 10, type: OBJID, value:
//     NOTIFICATION-LOG-MIB::notificationLogMIB");
// }

TEST_F(SessionBaseTest, TestGetSingleMib) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");

   // First get the current value and verify args
   auto initial_result = session.get("SNMPv2-MIB::sysLocation.0");
   ASSERT_FALSE(initial_result.empty());
   EXPECT_EQ(initial_result[0]._to_string(),
             "oid: SNMPv2-MIB::sysLocation, index: 0, type: STRING, value: my original location");

   auto get_args = session._get_args();
   std::vector<std::string> expected_get_args = {"-c",
                                                 "public",
                                                 "-r",
                                                 "3",
                                                 "-t",
                                                 "5",
                                                 "-v",
                                                 "2c",
                                                 "localhost:11161",
                                                 "SNMPv2-MIB::sysLocation.0"};
   ASSERT_EQ(get_args, expected_get_args);

   // Set the new value and verify args
   std::vector<std::string> set_mibs = {"SNMPv2-MIB::sysLocation.0", "s", "my newer location"};
   auto set_result = session.set(set_mibs);
   ASSERT_FALSE(set_result.empty());
   EXPECT_EQ(set_result[0]._to_string(),
             "oid: SNMPv2-MIB::sysLocation, index: 0, type: STRING, value: my newer location");

   auto set_args = session._get_args();
   std::vector<std::string> expected_set_args = {"-c",
                                                 "public",
                                                 "-r",
                                                 "3",
                                                 "-t",
                                                 "5",
                                                 "-v",
                                                 "2c",
                                                 "localhost:11161",
                                                 "SNMPv2-MIB::sysLocation.0",
                                                 "s",
                                                 "my newer location"};
   ASSERT_EQ(set_args, expected_set_args);

   // Verify the new value and args
   auto final_result = session.get("SNMPv2-MIB::sysLocation.0");
   ASSERT_FALSE(final_result.empty());
   EXPECT_EQ(final_result[0]._to_string(),
             "oid: SNMPv2-MIB::sysLocation, index: 0, type: STRING, value: my newer location");

   get_args = session._get_args();
   ASSERT_EQ(get_args, expected_get_args);

   // Set back to default and verify args
   set_mibs = {"SNMPv2-MIB::sysLocation.0", "s", "my original location"};
   set_result = session.set(set_mibs);
   ASSERT_FALSE(set_result.empty());
   EXPECT_EQ(set_result[0]._to_string(),
             "oid: SNMPv2-MIB::sysLocation, index: 0, type: STRING, value: my original location");

   set_args = session._get_args();
   expected_set_args = {"-c",
                        "public",
                        "-r",
                        "3",
                        "-t",
                        "5",
                        "-v",
                        "2c",
                        "localhost:11161",
                        "SNMPv2-MIB::sysLocation.0",
                        "s",
                        "my original location"};
   ASSERT_EQ(set_args, expected_set_args);
}

TEST_F(SessionBaseTest, TestGetV3MD5DES) {
   SessionBase session("localhost", "11161", "3", "", "MD5", "auth_pass", "", "", "authPriv", "",
                       "initial_md5_des", "DES", "priv_pass", "", "3", "5");
   auto result = session.get("SNMPv2-MIB::sysLocation.0");
   ASSERT_FALSE(result.empty());
   EXPECT_EQ(result[0]._to_string(),
             "oid: SNMPv2-MIB::sysLocation, index: 0, type: STRING, value: my original location");
}

TEST_F(SessionBaseTest, TestGetV3SHAAES) {
   SessionBase session("localhost", "11161", "3", "", "SHA", "auth_second", "", "", "authPriv", "",
                       "secondary_sha_aes", "AES", "priv_second", "", "3", "5");
   auto result = session.get("SNMPv2-MIB::sysLocation.0");
   ASSERT_FALSE(result.empty());
   EXPECT_EQ(result[0]._to_string(),
             "oid: SNMPv2-MIB::sysLocation, index: 0, type: STRING, value: my original location");
}

TEST_F(SessionBaseTest, TestGetV3SHANoPriv) {
   SessionBase session("localhost", "11161", "3", "", "SHA", "auth_second", "", "", "authNoPriv",
                       "", "secondary_sha_no_priv", "", "", "", "3", "5");
   auto result = session.get("SNMPv2-MIB::sysLocation.0");
   ASSERT_FALSE(result.empty());
   EXPECT_EQ(result[0]._to_string(),
             "oid: SNMPv2-MIB::sysLocation, index: 0, type: STRING, value: my original location");
}

TEST_F(SessionBaseTest, TestSet) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");
   std::vector<std::string> mibs = {"SNMPv2-MIB::sysContact.0", "s", "contact@example.com"};

   EXPECT_THROW(
       {
          try {
             auto result = session.set(mibs);
          } catch (PacketErrorBase const& e) {
             EXPECT_STREQ(e.what(),
                          "Error in packet.\nReason: notWritable (That object does not support "
                          "modification)\nFailed object: SNMPv2-MIB::sysContact.0\n\n");
             throw;
          }
       },
       PacketErrorBase);
}

TEST_F(SessionBaseTest, TestGetMultipleMibs) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");

   std::vector<std::string> mibs = {"SNMPv2-MIB::sysORDescr.1", "SNMPv2-MIB::sysORDescr.2",
                                    "SNMPv2-MIB::sysORDescr.3"};

   auto results = session.get(mibs);
   ASSERT_EQ(results.size(), 3);

// Verify individual results
#ifdef __APPLE__
   EXPECT_EQ(results[0]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 1, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(results[1]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 2, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(results[2]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 3, type: STRING, value: The SNMP Management "
             "Architecture MIB.");
#else
   EXPECT_EQ(results[0]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 1, type: STRING, value: The SNMP Management "
             "Architecture MIB.");
   EXPECT_EQ(results[1]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 2, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(results[2]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 3, type: STRING, value: The management "
             "information definitions for the SNMP User-based Security Model.");
#endif

   // Verify the constructed arguments
   auto args = session._get_args();
   std::vector<std::string> expected_args = {"-c",
                                             "public",
                                             "-r",
                                             "3",
                                             "-t",
                                             "5",
                                             "-v",
                                             "2c",
                                             "localhost:11161",
                                             "SNMPv2-MIB::sysORDescr.1",
                                             "SNMPv2-MIB::sysORDescr.2",
                                             "SNMPv2-MIB::sysORDescr.3"};
   ASSERT_EQ(args, expected_args);
}

TEST_F(SessionBaseTest, TestGetNext) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");

   std::vector<std::string> mibs = {"SNMPv2-MIB::sysORDescr.1", "SNMPv2-MIB::sysORDescr.2",
                                    "SNMPv2-MIB::sysORDescr.3"};

   auto results = session.get_next(mibs);
   ASSERT_EQ(results.size(), 3);

// Verify individual results
#ifdef __APPLE__
   EXPECT_EQ(results[0]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 2, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(results[1]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 3, type: STRING, value: The SNMP Management "
             "Architecture MIB.");
   EXPECT_EQ(results[2]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 4, type: STRING, value: The MIB modules for "
             "managing SNMP Notification, plus filtering.");
#else
   EXPECT_EQ(results[0]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 2, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(results[1]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 3, type: STRING, value: The management "
             "information definitions for the SNMP User-based Security Model.");
   EXPECT_EQ(results[2]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 4, type: STRING, value: The MIB module for "
             "SNMPv2 entities");
#endif

   // Verify the constructed arguments
   auto args = session._get_args();
   std::vector<std::string> expected_args = {"-c",
                                             "public",
                                             "-r",
                                             "3",
                                             "-t",
                                             "5",
                                             "-v",
                                             "2c",
                                             "localhost:11161",
                                             "SNMPv2-MIB::sysORDescr.1",
                                             "SNMPv2-MIB::sysORDescr.2",
                                             "SNMPv2-MIB::sysORDescr.3"};
   ASSERT_EQ(args, expected_args);
}

TEST_F(SessionBaseTest, TestGetNextEmptyMibs) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");

   std::vector<std::string> mibs;
   EXPECT_THROW(
       {
          try {
             auto results = session.get_next(mibs);
          } catch (GenericErrorBase const& e) {
             EXPECT_STREQ("Missing object name\n", e.what());
             throw;
          }
       },
       GenericErrorBase);
}
TEST_F(SessionBaseTest, TestBulkGet) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");

   std::vector<std::string> mibs = {"SNMPv2-MIB::sysORDescr", "sysORDescr", ".1.3.6.1.2.1.1.9.1.3"};

   auto results = session.bulk_get(mibs);
   ASSERT_EQ(results.size(), 30);

// Verify first set of results
#ifdef __APPLE__
   EXPECT_EQ(results[0]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 1, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(results[1]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 1, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(results[2]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 1, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(results[3]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 2, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(results[4]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 2, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(results[5]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 2, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(results[6]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 3, type: STRING, value: The SNMP Management "
             "Architecture MIB.");
   EXPECT_EQ(results[7]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 3, type: STRING, value: The SNMP Management "
             "Architecture MIB.");
   EXPECT_EQ(results[8]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 3, type: STRING, value: The SNMP Management "
             "Architecture MIB.");
   EXPECT_EQ(results[9]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 4, type: STRING, value: The MIB modules for "
             "managing SNMP Notification, plus filtering.");
   EXPECT_EQ(results[10]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 4, type: STRING, value: The MIB modules for "
             "managing SNMP Notification, plus filtering.");
   EXPECT_EQ(results[11]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 4, type: STRING, value: The MIB modules for "
             "managing SNMP Notification, plus filtering.");
   EXPECT_EQ(results[12]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 5, type: STRING, value: The MIB module for "
             "logging SNMP Notifications.");
   EXPECT_EQ(results[13]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 5, type: STRING, value: The MIB module for "
             "logging SNMP Notifications.");
   EXPECT_EQ(results[14]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 5, type: STRING, value: The MIB module for "
             "logging SNMP Notifications.");
   EXPECT_EQ(results[15]._to_string(),
             "oid: SNMPv2-MIB::sysORUpTime, index: 1, type: Timeticks, value: (0) 0:00:00.00");
   EXPECT_EQ(results[16]._to_string(),
             "oid: SNMPv2-MIB::sysORUpTime, index: 1, type: Timeticks, value: (0) 0:00:00.00");
   EXPECT_EQ(results[17]._to_string(),
             "oid: SNMPv2-MIB::sysORUpTime, index: 1, type: Timeticks, value: (0) 0:00:00.00");
   EXPECT_EQ(results[18]._to_string(),
             "oid: SNMPv2-MIB::sysORUpTime, index: 2, type: Timeticks, value: (0) 0:00:00.00");
   EXPECT_EQ(results[19]._to_string(),
             "oid: SNMPv2-MIB::sysORUpTime, index: 2, type: Timeticks, value: (0) 0:00:00.00");
   EXPECT_EQ(results[20]._to_string(),
             "oid: SNMPv2-MIB::sysORUpTime, index: 2, type: Timeticks, value: (0) 0:00:00.00");
   EXPECT_EQ(results[21]._to_string(),
             "oid: SNMPv2-MIB::sysORUpTime, index: 3, type: Timeticks, value: (0) 0:00:00.00");
   EXPECT_EQ(results[22]._to_string(),
             "oid: SNMPv2-MIB::sysORUpTime, index: 3, type: Timeticks, value: (0) 0:00:00.00");
   EXPECT_EQ(results[23]._to_string(),
             "oid: SNMPv2-MIB::sysORUpTime, index: 3, type: Timeticks, value: (0) 0:00:00.00");
   EXPECT_EQ(results[24]._to_string(),
             "oid: SNMPv2-MIB::sysORUpTime, index: 4, type: Timeticks, value: (0) 0:00:00.00");
   EXPECT_EQ(results[25]._to_string(),
             "oid: SNMPv2-MIB::sysORUpTime, index: 4, type: Timeticks, value: (0) 0:00:00.00");
   EXPECT_EQ(results[26]._to_string(),
             "oid: SNMPv2-MIB::sysORUpTime, index: 4, type: Timeticks, value: (0) 0:00:00.00");
   EXPECT_EQ(results[27]._to_string(),
             "oid: SNMPv2-MIB::sysORUpTime, index: 5, type: Timeticks, value: (0) 0:00:00.00");
   EXPECT_EQ(results[28]._to_string(),
             "oid: SNMPv2-MIB::sysORUpTime, index: 5, type: Timeticks, value: (0) 0:00:00.00");
   EXPECT_EQ(results[29]._to_string(),
             "oid: SNMPv2-MIB::sysORUpTime, index: 5, type: Timeticks, value: (0) 0:00:00.00");
#else
   EXPECT_EQ(results[0]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 1, type: STRING, value: The SNMP Management "
             "Architecture MIB.");
   EXPECT_EQ(results[1]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 1, type: STRING, value: The SNMP Management "
             "Architecture MIB.");
   EXPECT_EQ(results[2]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 1, type: STRING, value: The SNMP Management "
             "Architecture MIB.");
   EXPECT_EQ(results[3]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 2, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(results[4]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 2, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(results[5]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 2, type: STRING, value: The MIB for Message "
             "Processing and Dispatching.");
   EXPECT_EQ(results[6]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 3, type: STRING, value: The management "
             "information definitions for the SNMP User-based Security Model.");
   EXPECT_EQ(results[7]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 3, type: STRING, value: The management "
             "information definitions for the SNMP User-based Security Model.");
   EXPECT_EQ(results[8]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 3, type: STRING, value: The management "
             "information definitions for the SNMP User-based Security Model.");
   EXPECT_EQ(results[9]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 4, type: STRING, value: The MIB module for "
             "SNMPv2 entities");
   EXPECT_EQ(results[10]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 4, type: STRING, value: The MIB module for "
             "SNMPv2 entities");
   EXPECT_EQ(results[11]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 4, type: STRING, value: The MIB module for "
             "SNMPv2 entities");
   EXPECT_EQ(results[12]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 5, type: STRING, value: View-based Access "
             "Control Model for SNMP.");
   EXPECT_EQ(results[13]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 5, type: STRING, value: View-based Access "
             "Control Model for SNMP.");
   EXPECT_EQ(results[14]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 5, type: STRING, value: View-based Access "
             "Control Model for SNMP.");
   EXPECT_EQ(results[15]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 6, type: STRING, value: The MIB module for "
             "managing TCP implementations");
   EXPECT_EQ(results[16]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 6, type: STRING, value: The MIB module for "
             "managing TCP implementations");
   EXPECT_EQ(results[17]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 6, type: STRING, value: The MIB module for "
             "managing TCP implementations");
   EXPECT_EQ(results[18]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 7, type: STRING, value: The MIB module for "
             "managing UDP implementations");
   EXPECT_EQ(results[19]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 7, type: STRING, value: The MIB module for "
             "managing UDP implementations");
   EXPECT_EQ(results[20]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 7, type: STRING, value: The MIB module for "
             "managing UDP implementations");
   EXPECT_EQ(results[21]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 8, type: STRING, value: The MIB module for "
             "managing IP and ICMP implementations");
   EXPECT_EQ(results[22]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 8, type: STRING, value: The MIB module for "
             "managing IP and ICMP implementations");
   EXPECT_EQ(results[23]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 8, type: STRING, value: The MIB module for "
             "managing IP and ICMP implementations");
   EXPECT_EQ(results[24]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 9, type: STRING, value: The MIB modules for "
             "managing SNMP Notification, plus filtering.");
   EXPECT_EQ(results[25]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 9, type: STRING, value: The MIB modules for "
             "managing SNMP Notification, plus filtering.");
   EXPECT_EQ(results[26]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 9, type: STRING, value: The MIB modules for "
             "managing SNMP Notification, plus filtering.");
   EXPECT_EQ(results[27]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 10, type: STRING, value: The MIB module for "
             "logging SNMP Notifications.");
   EXPECT_EQ(results[28]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 10, type: STRING, value: The MIB module for "
             "logging SNMP Notifications.");
   EXPECT_EQ(results[29]._to_string(),
             "oid: SNMPv2-MIB::sysORDescr, index: 10, type: STRING, value: The MIB module for "
             "logging SNMP Notifications.");
#endif

   // Verify the constructed arguments
   auto args = session._get_args();
   std::vector<std::string> expected_args = {"-c",
                                             "public",
                                             "-r",
                                             "3",
                                             "-t",
                                             "5",
                                             "-v",
                                             "2c",
                                             "localhost:11161",
                                             "SNMPv2-MIB::sysORDescr",
                                             "sysORDescr",
                                             ".1.3.6.1.2.1.1.9.1.3"};
   ASSERT_EQ(args, expected_args);
}
TEST_F(SessionBaseTest, TestBulkGetEmptyMibs) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");

   std::vector<std::string> mibs;
   auto results = session.bulk_get(mibs);
   EXPECT_TRUE(results.empty());

   // Verify the constructed arguments
   auto args = session._get_args();
   std::vector<std::string> expected_args = {"-c", "public",         "-r", "3", "-t", "5", "-v",
                                             "2c", "localhost:11161"};
   ASSERT_EQ(args, expected_args);
}

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
          /* print_timeticks_numerically */ print_opts.print_timeticks_numerically);

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
         EXPECT_EQ(
             results[0]._to_string(),
             "oid: DISMAN-EXPRESSION-MIB::sysUpTimeInstance, index: , type: INTEGER, value: 46090");
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
          /* print_timeticks_numerically */ print_opts.print_timeticks_numerically);

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
         EXPECT_EQ(
             results[0]._to_string(),
             "oid: DISMAN-EXPRESSION-MIB::sysUpTimeInstance, index: , type: 46090, value: 46090");
      } else {
         // Verify get output with print options
         auto results = session.get("ifAdminStatus.1");

         ASSERT_EQ(results.size(), 1);
         EXPECT_EQ(results[0]._to_string(), print_opts.expected_get_output[0]);
      }
   }
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
                         {"oid: IF-MIB::ifAdminStatus, index: 1, type: INTEGER, value: up(1)"}},

            PrintOptions{// Case 2: enums true, others false
                         true,
                         false,
                         false,
                         false,
                         {"e"},
                         {"oid: IF-MIB::ifAdminStatus, index: 1, type: INTEGER, value: 1"}},

            PrintOptions{
                // Case 3: full_oids true, others false
                false,
                true,
                false,
                false,
                {"f"},
                {"oid: .iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifAdminStatus, "
                 "index: 1, type: INTEGER, value: up(1)"}},

            PrintOptions{// Case 4: oids_numeric true, others false
                         false,
                         false,
                         true,
                         false,
                         {"n"},
                         {"oid: .1.3.6.1.2.1.2.2.1.7, index: 1, type: INTEGER, value: up(1)"}},

            PrintOptions{
                // Case 5: enums and full_oids true, oids_numeric false
                true,
                true,
                false,
                false,
                {"e", "f"},
                {"oid: .iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifAdminStatus, "
                 "index: 1, type: INTEGER, value: 1"}},

            PrintOptions{// Case 6: enums and oids_numeric true, full_oids false
                         true,
                         false,
                         true,
                         false,
                         {"e", "n"},
                         {"oid: .1.3.6.1.2.1.2.2.1.7, index: 1, type: INTEGER, value: 1"}},

            PrintOptions{// Case 7: full_oids and oids_numeric true, enums false
                         false,
                         true,
                         true,
                         false,
                         {"f", "n"},
                         {"oid: .1.3.6.1.2.1.2.2.1.7, index: 1, type: INTEGER, value: up(1)"}},

            PrintOptions{// Case 8: All true except timeticks numeric
                         true,
                         true,
                         true,
                         false,
                         {"e", "f", "n"},
                         {"oid: .1.3.6.1.2.1.2.2.1.7, index: 1, type: INTEGER, value: 1"}},

            PrintOptions{// Case 9: Only timeticks numeric
                         false,
                         false,
                         false,
                         true,
                         {"t"},
                         {"oid: DISMAN-EXPRESSION-MIB::sysUpTimeInstance, index: , type: 46090, "
                          "value: 46090"}})));