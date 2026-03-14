#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmpwalk.h"

static int g_parse_args_result = NETSNMP_PARSE_ARGS_ERROR;

extern "C" int snmp_parse_args(int argc,
                                char **argv,
                                netsnmp_session *session,
                                const char *localOpts,
                                void (*proc)(int, char *const *, int)) {
   (void)argc;
   (void)argv;
   (void)session;
   (void)localOpts;
   (void)proc;
   return g_parse_args_result;
}

class SnmpWalkParseArgsShimTest : public ::testing::Test {};

TEST_F(SnmpWalkParseArgsShimTest, TestParseArgsErrorThrowsParseError) {
   g_parse_args_result = NETSNMP_PARSE_ARGS_ERROR;
   std::vector<std::string> args;

   EXPECT_THROW(
       {
          try {
             auto results = snmpwalk(args, "testing_walk_parse_args_error");
          } catch (ParseErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("NETSNMP_PARSE_ARGS_ERROR") != std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}

TEST_F(SnmpWalkParseArgsShimTest, TestParseArgsSuccessExitThrowsParseError) {
   g_parse_args_result = NETSNMP_PARSE_ARGS_SUCCESS_EXIT;
   std::vector<std::string> args;

   EXPECT_THROW(
       {
          try {
             auto results = snmpwalk(args, "testing_walk_parse_args_success_exit");
          } catch (ParseErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("NETSNMP_PARSE_ARGS_SUCCESS_EXIT") != std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}
