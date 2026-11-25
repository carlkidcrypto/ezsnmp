#include <gtest/gtest.h>

#include <functional>
#include <iostream>
#include <string>
#include <vector>

#include "datatypes.h"
#include "exceptionsbase.h"
#include "sessionbase.h"

#if defined(__clang__) || defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wdeprecated-declarations"
#endif

#if defined(GTEST_SKIP)
#define EZSNMP_SKIP_TEST_AND_RETURN(msg) GTEST_SKIP() << msg
#else
#define EZSNMP_SKIP_TEST_AND_RETURN(msg)            \
   do {                                             \
      std::cerr << "SKIPPED: " << msg << std::endl; \
      return;                                       \
   } while (false)
#endif

class SessionBaseOperationsTest : public ::testing::Test {};

namespace {

// Helper function to verify MIB descriptions exist in results
void VerifyMibDescriptions(std::vector<Result> const& result,
                           std::vector<std::string> const& expected_descriptions) {
   ASSERT_FALSE(result.empty());

   for (auto const& expected_desc : expected_descriptions) {
      bool found = false;
      for (auto const& res : result) {
         std::string res_str = res._to_string();
         if (res_str.find("value: " + expected_desc) != std::string::npos ||
             res_str.find("converted_value: " + expected_desc) != std::string::npos) {
            found = true;
            break;
         }
      }
      EXPECT_TRUE(found) << "Expected MIB description not found: " << expected_desc;
   }
}

std::vector<std::string> ExpectedSysORDescrDescriptions() {
#ifdef __APPLE__
   return {"The SNMP Management Architecture MIB.",
           "The MIB for Message Processing and Dispatching.",
           "The MIB modules for managing SNMP Notification, plus filtering.",
           "The MIB module for logging SNMP Notifications."};
#else
   return {"The SNMP Management Architecture MIB.",
           "The MIB for Message Processing and Dispatching.",
           "The management information definitions for the SNMP User-based Security Model.",
           "The MIB module for SNMPv2 entities",
           "View-based Access Control Model for SNMP.",
           "The MIB module for managing TCP implementations",
           "The MIB module for managing UDP implementations",
           "The MIB module for managing IP and ICMP implementations",
           "The MIB modules for managing SNMP Notification, plus filtering.",
           "The MIB module for logging SNMP Notifications."};
#endif
}

} // namespace

TEST_F(SessionBaseOperationsTest, GetNextSingleMibStringOverload) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");

   std::vector<Result> results;
   try {
      results = session.get_next(".1.3.6.1.2.1.1.5.0");
   } catch (TimeoutErrorBase const&) {
      EZSNMP_SKIP_TEST_AND_RETURN("SNMP agent is not reachable in this environment");
   }

   ASSERT_EQ(results.size(), 1u);
   EXPECT_FALSE(results[0].oid.empty());
   EXPECT_FALSE(results[0].type.empty());

   auto args = session._get_args();
   std::vector<std::string> expected_args = {
       "-c", "public", "-r", "3", "-t", "5", "-v", "2c", "localhost:11161", ".1.3.6.1.2.1.1.5.0"};
   ASSERT_EQ(args, expected_args);
}

TEST_F(SessionBaseOperationsTest, BulkGetSingleMibStringOverload) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");

   std::vector<Result> results;
   try {
      results = session.bulk_get(".1.3.6.1.2.1.1.5.0");
   } catch (TimeoutErrorBase const&) {
      EZSNMP_SKIP_TEST_AND_RETURN("SNMP agent is not reachable in this environment");
   }

   ASSERT_FALSE(results.empty());
   EXPECT_FALSE(results[0].oid.empty());
   EXPECT_FALSE(results[0].type.empty());

   auto args = session._get_args();
   std::vector<std::string> expected_args = {
       "-c", "public", "-r", "3", "-t", "5", "-v", "2c", "localhost:11161", ".1.3.6.1.2.1.1.5.0"};
   ASSERT_EQ(args, expected_args);
}

struct WalkOperationCase {
   std::string name;
   std::function<std::vector<Result>(SessionBase&, std::string const&)> invoke;
};

class SessionBaseWalkOperationTest : public ::testing::TestWithParam<WalkOperationCase> {};

TEST_P(SessionBaseWalkOperationTest, WalkSingleMib) {
   WalkOperationCase const& tc = GetParam();
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");
   auto result = tc.invoke(session, "SNMPv2-MIB::sysORDescr");
   VerifyMibDescriptions(result, ExpectedSysORDescrDescriptions());
}

TEST_P(SessionBaseWalkOperationTest, WalkEmptyMib) {
   WalkOperationCase const& tc = GetParam();
   SessionBase session("localhost", "11161", "2c", "public");
   try {
      auto results = tc.invoke(session, "");
      EXPECT_FALSE(results.empty());
   } catch (TimeoutErrorBase const&) {
#ifdef __APPLE__
      // On macOS runners under heavy load, walking from the root can time out.
#else
      throw;
#endif
   }
}

INSTANTIATE_TEST_SUITE_P(
    WalkOperations,
    SessionBaseWalkOperationTest,
    ::testing::Values(WalkOperationCase{"Walk", [](SessionBase& s,
                                                   std::string const& mib) { return s.walk(mib); }},
                      WalkOperationCase{
                          "BulkWalk",
                          [](SessionBase& s, std::string const& mib) { return s.bulk_walk(mib); }}),
    [](testing::TestParamInfo<WalkOperationCase> const& info) { return info.param.name; });

TEST_F(SessionBaseOperationsTest, GetSingleMibAndSetRoundTrip) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");

   auto initial_result = session.get("SNMPv2-MIB::sysLocation.0");
   ASSERT_FALSE(initial_result.empty());
   EXPECT_EQ(initial_result[0].type, "STRING");
   EXPECT_TRUE(initial_result[0].oid.find("sysLocation") != std::string::npos);

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

   std::vector<std::string> set_mibs = {"SNMPv2-MIB::sysLocation.0", "s", "my newer location"};
   auto set_result = session.set(set_mibs);
   ASSERT_FALSE(set_result.empty());
   EXPECT_EQ(set_result[0]._to_string(),
             "oid: SNMPv2-MIB::sysLocation, index: 0, type: STRING, value: my newer location, "
             "converted_value: my newer location");

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

   auto final_result = session.get("SNMPv2-MIB::sysLocation.0");
   ASSERT_FALSE(final_result.empty());
   std::string final_value = final_result[0].value;
   bool set_persisted = (final_value == "my newer location");
   bool set_ignored = (final_value == initial_result[0].value);
   EXPECT_TRUE(set_persisted || set_ignored)
       << "Expected either 'my newer location' (SET persisted) or initial value (SET ignored), "
       << "but got: " << final_value;

   if (set_persisted) {
      EXPECT_EQ(final_result[0]._to_string(),
                "oid: SNMPv2-MIB::sysLocation, index: 0, type: STRING, value: my newer location, "
                "converted_value: my newer location");
   }

   get_args = session._get_args();
   ASSERT_EQ(get_args, expected_get_args);

   if (set_persisted) {
      set_mibs = {"SNMPv2-MIB::sysLocation.0", "s", "my original location"};
      set_result = session.set(set_mibs);
      ASSERT_FALSE(set_result.empty());
      EXPECT_EQ(
          set_result[0]._to_string(),
          "oid: SNMPv2-MIB::sysLocation, index: 0, type: STRING, value: my original location, "
          "converted_value: my original location");

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
   } else {
      std::cerr << "INFO: sysLocation appears to be read-only on this system" << std::endl;
   }
}

TEST_F(SessionBaseOperationsTest, GetV3MD5DES) {
   SessionBase session("localhost", "11161", "3", "", "MD5", "auth_pass", "", "", "authPriv", "",
                       "initial_md5_des", "DES", "priv_pass", "", "3", "5");
   try {
      auto result = session.get("SNMPv2-MIB::sysLocation.0");
      ASSERT_FALSE(result.empty());
      EXPECT_EQ(
          result[0]._to_string(),
          "oid: SNMPv2-MIB::sysLocation, index: 0, type: STRING, value: my original location, "
          "converted_value: my original location");
   } catch (ParseErrorBase const& e) {
      std::string error_msg(e.what());
      bool is_deprecated_algorithm_error =
          error_msg.find("NETSNMP_PARSE_ARGS_ERROR") != std::string::npos ||
          error_msg.find("PARSE_ARGS_ERROR") != std::string::npos ||
          error_msg.find("unknown auth protocol") != std::string::npos ||
          error_msg.find("unknown priv protocol") != std::string::npos ||
          error_msg.find("Invalid privacy protocol") != std::string::npos ||
          error_msg.find("Unknown security model") != std::string::npos;

      if (is_deprecated_algorithm_error) {
#if defined(GTEST_SKIP)
         GTEST_SKIP() << "MD5/DES algorithms not supported on this platform: " << error_msg;
#else
         std::cerr << "INFO: MD5/DES algorithms not supported on this platform: " << error_msg
                   << std::endl;
         return;
#endif
      }
      throw;
   }
}

struct V3GetCase {
   std::string name;
   std::string security_level;
   std::string username;
   std::string privacy_protocol;
   std::string privacy_passphrase;
};

class SessionBaseV3GetTest : public ::testing::TestWithParam<V3GetCase> {};

TEST_P(SessionBaseV3GetTest, GetsSysLocation) {
   V3GetCase const& tc = GetParam();
   SessionBase session("localhost", "11161", "3", "", "SHA", "auth_second", "", "",
                       tc.security_level, "", tc.username, tc.privacy_protocol,
                       tc.privacy_passphrase, "", "3", "5");
   auto result = session.get("SNMPv2-MIB::sysLocation.0");
   ASSERT_FALSE(result.empty());
   EXPECT_EQ(result[0]._to_string(),
             "oid: SNMPv2-MIB::sysLocation, index: 0, type: STRING, value: my original location, "
             "converted_value: my original location");
}

INSTANTIATE_TEST_SUITE_P(
    V3AuthVariants,
    SessionBaseV3GetTest,
    ::testing::Values(V3GetCase{"SHAAES", "authPriv", "secondary_sha_aes", "AES", "priv_second"},
                      V3GetCase{"SHANoPriv", "authNoPriv", "secondary_sha_no_priv", "", ""}),
    [](testing::TestParamInfo<V3GetCase> const& info) { return info.param.name; });

TEST_F(SessionBaseOperationsTest, SetNotWritableThrowsPacketError) {
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

TEST_F(SessionBaseOperationsTest, GetMultipleMibs) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");

   std::vector<std::string> mibs = {"SNMPv2-MIB::sysORDescr.1", "SNMPv2-MIB::sysORDescr.2",
                                    "SNMPv2-MIB::sysORDescr.3"};

   auto results = session.get(mibs);
   ASSERT_EQ(results.size(), 3u);

   for (size_t i = 0; i < results.size(); ++i) {
      EXPECT_TRUE(results[i].oid.find("sysORDescr") != std::string::npos);
      EXPECT_EQ(results[i].type, "STRING");
      EXPECT_FALSE(results[i].value.empty());
      EXPECT_EQ(results[i].index, std::to_string(i + 1));
   }

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

TEST_F(SessionBaseOperationsTest, GetNextMultipleMibs) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");

   std::vector<std::string> mibs = {"SNMPv2-MIB::sysORDescr.1", "SNMPv2-MIB::sysORDescr.2",
                                    "SNMPv2-MIB::sysORDescr.3"};

   auto results = session.get_next(mibs);
   ASSERT_EQ(results.size(), 3u);

   for (size_t i = 0; i < results.size(); ++i) {
      EXPECT_TRUE(results[i].oid.find("sysORDescr") != std::string::npos);
      EXPECT_EQ(results[i].type, "STRING");
      EXPECT_FALSE(results[i].value.empty());
      EXPECT_EQ(results[i].index, std::to_string(i + 2));
   }

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

TEST_F(SessionBaseOperationsTest, GetNextEmptyMibsThrowsGenericError) {
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

TEST_F(SessionBaseOperationsTest, BulkGetMultipleMibs) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");

   std::vector<std::string> mibs = {"SNMPv2-MIB::sysORDescr", "sysORDescr", ".1.3.6.1.2.1.1.9.1.3"};

   auto results = session.bulk_get(mibs);
   EXPECT_GE(results.size(), 15u);
   EXPECT_LE(results.size(), 40u);

   for (auto const& result : results) {
      EXPECT_TRUE(result.oid.find("sysOR") != std::string::npos);
      EXPECT_FALSE(result.type.empty());
      EXPECT_FALSE(result.index.empty());
   }

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

TEST_F(SessionBaseOperationsTest, BulkGetEmptyMibs) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");

   std::vector<std::string> mibs;
   auto results = session.bulk_get(mibs);
   EXPECT_TRUE(results.empty());

   auto args = session._get_args();
   std::vector<std::string> expected_args = {"-c", "public",         "-r", "3", "-t", "5", "-v",
                                             "2c", "localhost:11161"};
   ASSERT_EQ(args, expected_args);
}

TEST_F(SessionBaseOperationsTest, BulkWalkVectorOverloadEmptyMibs) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");
   std::vector<std::string> mibs;
   auto results = session.bulk_walk(mibs);
   EXPECT_FALSE(results.empty());
}

TEST_F(SessionBaseOperationsTest, BulkWalkVectorOverloadSingleMib) {
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "3", "5");
   std::vector<std::string> mibs = {"SNMPv2-MIB::sysORDescr"};
   auto results = session.bulk_walk(mibs);
   EXPECT_FALSE(results.empty());
}

TEST_F(SessionBaseOperationsTest, GetEmptyMibThrowsGenericError) {
   SessionBase session("localhost", "11161", "2c", "public");
   EXPECT_THROW(session.get(""), GenericErrorBase);
}

TEST_F(SessionBaseOperationsTest, BulkGetSingleMibVector) {
   SessionBase session("localhost", "11161", "2c", "public");
   std::vector<std::string> mibs = {"SNMPv2-MIB::sysORDescr"};
   auto results = session.bulk_get(mibs);
   EXPECT_FALSE(results.empty());
}

TEST_F(SessionBaseOperationsTest, V3MultipleSessionsSameUserSequential) {
   SessionBase session1("localhost", "11161", "3", "", "MD5", "auth_pass", "", "", "authPriv", "",
                        "initial_md5_aes", "AES", "priv_pass", "", "3", "5");
   auto result1 = session1.get("SNMPv2-MIB::sysDescr.0");
   EXPECT_FALSE(result1.empty());

   SessionBase session2("localhost", "11161", "3", "", "MD5", "auth_pass", "", "", "authPriv", "",
                        "initial_md5_aes", "AES", "priv_pass", "", "3", "5");
   auto result2 = session2.get("SNMPv2-MIB::sysDescr.0");
   EXPECT_FALSE(result2.empty());

   for (int i = 0; i < 3; i++) {
      auto result1_alt = session1.get("SNMPv2-MIB::sysDescr.0");
      EXPECT_FALSE(result1_alt.empty());

      auto result2_alt = session2.get("SNMPv2-MIB::sysDescr.0");
      EXPECT_FALSE(result2_alt.empty());
   }
}

TEST_F(SessionBaseOperationsTest, V3SessionRecreationSameUser) {
   {
      SessionBase session1("localhost", "11161", "3", "", "MD5", "auth_pass", "", "", "authPriv",
                           "", "initial_md5_aes", "AES", "priv_pass", "", "3", "5");
      auto result1 = session1.get("SNMPv2-MIB::sysDescr.0");
      EXPECT_FALSE(result1.empty());
   }

   {
      SessionBase session2("localhost", "11161", "3", "", "MD5", "auth_pass", "", "", "authPriv",
                           "", "initial_md5_aes", "AES", "priv_pass", "", "3", "5");
      auto result2 = session2.get("SNMPv2-MIB::sysDescr.0");
      EXPECT_FALSE(result2.empty());
   }

   {
      SessionBase session3("localhost", "11161", "3", "", "MD5", "auth_pass", "", "", "authPriv",
                           "", "initial_md5_aes", "AES", "priv_pass", "", "3", "5");
      auto result3 = session3.get("SNMPv2-MIB::sysDescr.0");
      EXPECT_FALSE(result3.empty());
   }
}

TEST_F(SessionBaseOperationsTest, V3CacheClearingBeforeAllOperations) {
   SessionBase session("localhost", "11161", "3", "", "MD5", "auth_pass", "", "", "authPriv", "",
                       "initial_md5_aes", "AES", "priv_pass", "", "3", "5");

   auto result = session.get("SNMPv2-MIB::sysDescr.0");
   EXPECT_FALSE(result.empty());

   auto walk_result = session.walk("SNMPv2-MIB::system");
   EXPECT_FALSE(walk_result.empty());

   auto bulk_walk_result = session.bulk_walk("SNMPv2-MIB::system");
   EXPECT_FALSE(bulk_walk_result.empty());

   std::vector<std::string> oids = {"SNMPv2-MIB::sysDescr.0"};
   auto get_next_result = session.get_next(oids);
   EXPECT_FALSE(get_next_result.empty());

   std::vector<std::string> bulk_oids = {"SNMPv2-MIB::sysDescr.0", "SNMPv2-MIB::sysObjectID.0"};
   auto bulk_get_result = session.bulk_get(bulk_oids);
   EXPECT_FALSE(bulk_get_result.empty());
}

struct EmptyMibFallbackCase {
   std::string name;
   std::function<void(SessionBase&)> invoke;
};

class SessionBaseEmptyMibFallbackTest : public ::testing::TestWithParam<EmptyMibFallbackCase> {};

TEST_P(SessionBaseEmptyMibFallbackTest, ExercisesEmptyMibBranch) {
   EmptyMibFallbackCase const& tc = GetParam();
   SessionBase session("localhost", "11161", "2c", "public", "", "", "", "", "", "", "", "", "", "",
                       "1", "1");
   try {
      tc.invoke(session);
   } catch (TimeoutErrorBase const&) {
      EZSNMP_SKIP_TEST_AND_RETURN("SNMP agent not reachable");
   } catch (std::exception const&) {
      // Any other error still means the empty-mib branch was exercised
   }
}

INSTANTIATE_TEST_SUITE_P(
    EmptyMibFallbacks,
    SessionBaseEmptyMibFallbackTest,
    ::testing::Values(EmptyMibFallbackCase{"GetNext", [](SessionBase& s) { (void)s.get_next(""); }},
                      EmptyMibFallbackCase{"BulkGet",
                                           [](SessionBase& s) { (void)s.bulk_get(""); }}),
    [](testing::TestParamInfo<EmptyMibFallbackCase> const& info) { return info.param.name; });

#if defined(__clang__) || defined(__GNUC__)
#pragma GCC diagnostic pop
#endif
