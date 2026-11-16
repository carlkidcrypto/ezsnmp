#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include "exceptionsbase.h"
#include "snmptrap.h"

void snmptrap_usage(void);
int snmp_input(int operation, netsnmp_session *session, int reqid, netsnmp_pdu *pdu, void *magic);

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

class SnmpTrapParseArgsShimTest : public ::testing::Test {};

TEST_F(SnmpTrapParseArgsShimTest, TestParseArgsErrorThrowsParseError) {
   g_parse_args_result = NETSNMP_PARSE_ARGS_ERROR;
   std::vector<std::string> args;

   EXPECT_THROW(
       {
          try {
             snmptrap(args, "testing_snmptrap_parse_args_error");
          } catch (ParseErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("NETSNMP_PARSE_ARGS_ERROR") != std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}

TEST_F(SnmpTrapParseArgsShimTest, TestParseArgsSuccessExitThrowsParseError) {
   g_parse_args_result = NETSNMP_PARSE_ARGS_SUCCESS_EXIT;
   std::vector<std::string> args;

   EXPECT_THROW(
       {
          try {
             snmptrap(args, "testing_snmptrap_parse_args_success_exit");
          } catch (ParseErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("NETSNMP_PARSE_ARGS_SUCCESS_EXIT") != std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}

TEST_F(SnmpTrapParseArgsShimTest, TestParseArgsErrorUsageThrowsParseError) {
   g_parse_args_result = NETSNMP_PARSE_ARGS_ERROR_USAGE;
   std::vector<std::string> args;

   EXPECT_THROW(
       {
          try {
             snmptrap(args, "testing_snmptrap_parse_args_error_usage");
          } catch (ParseErrorBase const &e) {
             std::string msg(e.what());
             EXPECT_TRUE(msg.find("NETSNMP_PARSE_ARGS_ERROR_USAGE") != std::string::npos);
             throw;
          }
       },
       ParseErrorBase);
}

TEST_F(SnmpTrapParseArgsShimTest, TestUsageDoesNotThrow) {
   EXPECT_NO_THROW({ snmptrap_usage(); });
}

TEST_F(SnmpTrapParseArgsShimTest, TestSnmpInputReturnsOne) {
   EXPECT_EQ(snmp_input(0, nullptr, 0, nullptr, nullptr), 1);
}
