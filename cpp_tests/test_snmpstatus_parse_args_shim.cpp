#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmpstatus.h"

static int g_parse_args_result = NETSNMP_PARSE_ARGS_ERROR;

extern "C" int snmp_parse_args(int argc,
                               char **argv,
                               netsnmp_session *session,
                               char const *localOpts,
                               void (*proc)(int, char *const *, int)) {
   (void)argc;
   (void)argv;
   (void)session;
   (void)localOpts;
   (void)proc;
   return g_parse_args_result;
}

class SnmpStatusParseArgsShimTest : public ::testing::Test {};

TEST_F(SnmpStatusParseArgsShimTest, TestParseArgsErrorThrowsParseError) {
   g_parse_args_result = NETSNMP_PARSE_ARGS_ERROR;
   std::vector<std::string> args;

   EXPECT_THROW(
       {
          try {
             auto results = snmpstatus(args, "testing_status_parse_args_error");
          } catch (ParseErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("NETSNMP_PARSE_ARGS_ERROR") != std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}

TEST_F(SnmpStatusParseArgsShimTest, TestParseArgsSuccessExitThrowsParseError) {
   g_parse_args_result = NETSNMP_PARSE_ARGS_SUCCESS_EXIT;
   std::vector<std::string> args;

   EXPECT_THROW(
       {
          try {
             auto results = snmpstatus(args, "testing_status_parse_args_success_exit");
          } catch (ParseErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("NETSNMP_PARSE_ARGS_SUCCESS_EXIT") != std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}
