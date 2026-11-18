#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

#include <cstring>
#include <string>
#include <vector>

#include "exceptionsbase.h"
#include "snmptable.h"
#include "test_snmp_response_helpers.h"

namespace {

enum class TableShimMode {
   GETBULK_NORMAL,
   GETBULK_LONG_VALUE,
   GETBULK_NOSUCHNAME,
   GETBULK_GENERR,
   GETBULK_TIMEOUT,
   GETBULK_STAT_ERROR,
   GETBULK_DUPLICATE_OID,
   GETNEXT_NORMAL,
   GETNEXT_MULTI_PASS,
   GETNEXT_NOSUCHNAME,
   GETNEXT_GENERR,
   GETNEXT_TIMEOUT,
   GETNEXT_STAT_ERROR,
};

TableShimMode g_mode = TableShimMode::GETBULK_NORMAL;
int g_call_count = 0;

void add_sysor_row(netsnmp_pdu *pdu,
                   oid index_val,
                   char const *descr,
                   long uptime_val,
                   bool include_descr = true,
                   bool include_extra_col = false) {
   oid id_oid[] = {1, 3, 6, 1, 2, 1, 1, 9, 1, 2, index_val};
   oid id_val[] = {1, 3, 6, 1, 2, 1, 1};
   snmp_varlist_add_variable(&pdu->variables, id_oid, OID_LENGTH(id_oid), ASN_OBJECT_ID,
                             reinterpret_cast<u_char *>(id_val), sizeof(id_val));

   if (include_descr) {
      oid descr_oid[] = {1, 3, 6, 1, 2, 1, 1, 9, 1, 3, index_val};
      snmp_varlist_add_variable(&pdu->variables, descr_oid, OID_LENGTH(descr_oid), ASN_OCTET_STR,
                                reinterpret_cast<u_char const *>(descr), std::strlen(descr));
   }

   oid up_oid[] = {1, 3, 6, 1, 2, 1, 1, 9, 1, 4, index_val};
   snmp_varlist_add_variable(&pdu->variables, up_oid, OID_LENGTH(up_oid), ASN_TIMETICKS,
                             reinterpret_cast<u_char *>(&uptime_val), sizeof(uptime_val));

   if (include_extra_col) {
      oid extra_oid[] = {1, 3, 6, 1, 2, 1, 1, 9, 1, 99, index_val};
      long extra_val = 42;
      snmp_varlist_add_variable(&pdu->variables, extra_oid, OID_LENGTH(extra_oid), ASN_INTEGER,
                                reinterpret_cast<u_char *>(&extra_val), sizeof(extra_val));
   }
}

void add_end_of_table_var(netsnmp_pdu *pdu) {
   oid end_oid[] = {1, 3, 6, 1, 2, 1, 2, 1, 0};
   long end_val = 1;
   snmp_varlist_add_variable(&pdu->variables, end_oid, OID_LENGTH(end_oid), ASN_INTEGER,
                             reinterpret_cast<u_char *>(&end_val), sizeof(end_val));
}

} // namespace

extern "C" int snmp_sess_synch_response(ezsnmp_test::session_handle sessp,
                                        netsnmp_pdu *pdu,
                                        netsnmp_pdu **response) {
   (void)sessp;
   (void)pdu;
   ++g_call_count;

   if (g_mode == TableShimMode::GETBULK_TIMEOUT || g_mode == TableShimMode::GETNEXT_TIMEOUT) {
      *response = nullptr;
      return STAT_TIMEOUT;
   }
   if (g_mode == TableShimMode::GETBULK_STAT_ERROR || g_mode == TableShimMode::GETNEXT_STAT_ERROR) {
      *response = nullptr;
      return STAT_ERROR;
   }

   netsnmp_pdu *resp = snmp_pdu_create(SNMP_MSG_RESPONSE);
   resp->errstat = SNMP_ERR_NOERROR;
   resp->errindex = 0;

   switch (g_mode) {
      case TableShimMode::GETBULK_NORMAL:
         if (g_call_count == 1) {
            add_sysor_row(resp, 1, "SNMPv2\nMIB", 123, true, true);
            add_sysor_row(resp, 2, "unused", 456, false, false);
         } else {
            add_end_of_table_var(resp);
         }
         break;

      case TableShimMode::GETBULK_LONG_VALUE:
         if (g_call_count == 1) {
            std::string long_descr(4500, 'A');
            add_sysor_row(resp, 1, long_descr.c_str(), 100, true, false);
         } else {
            add_end_of_table_var(resp);
         }
         break;

      case TableShimMode::GETBULK_NOSUCHNAME:
      case TableShimMode::GETNEXT_NOSUCHNAME:
         resp->errstat = SNMP_ERR_NOSUCHNAME;
         break;

      case TableShimMode::GETBULK_GENERR:
      case TableShimMode::GETNEXT_GENERR:
         snmp_free_pdu(resp);
         resp = make_snmp_generr_response();
         break;

      case TableShimMode::GETBULK_DUPLICATE_OID: {
         oid descr_oid[] = {1, 3, 6, 1, 2, 1, 1, 9, 1, 3, 1};
         char const *descr = "dup";
         snmp_varlist_add_variable(&resp->variables, descr_oid, OID_LENGTH(descr_oid),
                                   ASN_OCTET_STR, reinterpret_cast<u_char const *>(descr),
                                   std::strlen(descr));
         snmp_varlist_add_variable(&resp->variables, descr_oid, OID_LENGTH(descr_oid),
                                   ASN_OCTET_STR, reinterpret_cast<u_char const *>(descr),
                                   std::strlen(descr));
         break;
      }

      case TableShimMode::GETNEXT_NORMAL:
         if (g_call_count == 1) {
            add_sysor_row(resp, 1, "Row1\nDesc", 100, true, false);
         } else {
            add_end_of_table_var(resp);
         }
         break;

      case TableShimMode::GETNEXT_MULTI_PASS:
         if (g_call_count == 1) {
            add_sysor_row(resp, 1, "Row1", 100, true, false);
         } else if (g_call_count == 2) {
            add_sysor_row(resp, 2, "Row2", 200, true, false);
         } else {
            add_end_of_table_var(resp);
         }
         break;

      default:
         break;
   }

   *response = resp;
   return STAT_SUCCESS;
}

class SnmpTableWithDataShimTest : public ::testing::Test {
  protected:
   void SetUp() override {
      g_mode = TableShimMode::GETBULK_NORMAL;
      g_call_count = 0;
   }
   void TearDown() override {
      netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_EXTENDED_INDEX, 0);
      netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_OID_OUTPUT_FORMAT, 0);
   }
};

TEST_F(SnmpTableWithDataShimTest, TestGetBulkNormalAndExtraColumns) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   auto res = snmptable(args, "testing_table_getbulk_normal");
   ASSERT_EQ(res.size(), 1u);
   EXPECT_NE(res[0].find("SNMP table: SNMPv2-MIB::sysORTable"), std::string::npos);
   EXPECT_NE(res[0].find("SNMPv2 MIB"), std::string::npos);
   EXPECT_NE(res[0].find("?"), std::string::npos);
   EXPECT_NE(res[0].find("WARNING: More columns on agent than in MIB"), std::string::npos);
}

TEST_F(SnmpTableWithDataShimTest, TestGetBulkColumnWidthMaxWidthAndShowIndex) {
   std::vector<std::string> args = {"-Ci",
                                    "-Cl",
                                    "-Cc",
                                    "10",
                                    "-Cw",
                                    "25",
                                    "-Cr",
                                    "5",
                                    "-v",
                                    "2c",
                                    "-c",
                                    "public",
                                    "localhost:11161",
                                    "SNMPv2-MIB::sysORTable"};
   auto res = snmptable(args, "testing_table_col_max_idx");
   ASSERT_EQ(res.size(), 1u);
   EXPECT_NE(res[0].find("index: 1"), std::string::npos);
   EXPECT_NE(res[0].find("index: 2"), std::string::npos);
}

TEST_F(SnmpTableWithDataShimTest, TestGetBulkFieldSeparatorNoIndexAndNoHeaders) {
   std::vector<std::string> args = {
       "-CH", "-Cf", "|", "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   auto res = snmptable(args, "testing_table_sep_no_idx");
   ASSERT_EQ(res.size(), 1u);
   EXPECT_EQ(res[0].find("SNMP table:"), std::string::npos);
   EXPECT_NE(res[0].find("|"), std::string::npos);
}

TEST_F(SnmpTableWithDataShimTest, TestGetBulkShowIndexWithoutSeparator) {
   std::vector<std::string> args = {
       "-Ci", "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   auto res = snmptable(args, "testing_table_idx_default");
   ASSERT_EQ(res.size(), 1u);
   EXPECT_NE(res[0].find("index"), std::string::npos);
}

TEST_F(SnmpTableWithDataShimTest, TestGetBulkOutputFormatsForExtractIndex) {
   for (std::string const &opt : {"-Os", "-Of", "-Ou", "-OS", "-OX"}) {
      g_call_count = 0;
      std::vector<std::string> args = {
          opt, "-Ci", "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
      auto res = snmptable(args, "testing_table_out_fmt");
      ASSERT_EQ(res.size(), 1u);
   }
}

TEST_F(SnmpTableWithDataShimTest, TestGetBulkLongValueTriggersLargeBuffer) {
   g_mode = TableShimMode::GETBULK_LONG_VALUE;
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   auto res = snmptable(args, "testing_table_long_val");
   ASSERT_EQ(res.size(), 1u);
   EXPECT_NE(res[0].find(std::string(100, 'A')), std::string::npos);
}

TEST_F(SnmpTableWithDataShimTest, TestGetBulkNoSuchName) {
   g_mode = TableShimMode::GETBULK_NOSUCHNAME;
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   auto res = snmptable(args, "testing_table_bulk_nosuchname");
   ASSERT_EQ(res.size(), 1u);
   EXPECT_NE(res[0].find("End of MIB"), std::string::npos);
   EXPECT_NE(res[0].find("No entries"), std::string::npos);
}

TEST_F(SnmpTableWithDataShimTest, TestGetBulkGenErrThrowsPacketError) {
   g_mode = TableShimMode::GETBULK_GENERR;
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   EXPECT_THROW(snmptable(args, "testing_table_bulk_generr"), PacketErrorBase);
}

TEST_F(SnmpTableWithDataShimTest, TestGetBulkTimeoutThrowsTimeoutError) {
   g_mode = TableShimMode::GETBULK_TIMEOUT;
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   EXPECT_THROW(snmptable(args, "testing_table_bulk_timeout"), TimeoutErrorBase);
}

TEST_F(SnmpTableWithDataShimTest, TestGetBulkStatErrorThrowsException) {
   g_mode = TableShimMode::GETBULK_STAT_ERROR;
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   EXPECT_THROW(snmptable(args, "testing_table_bulk_staterr"), GenericErrorBase);
}

TEST_F(SnmpTableWithDataShimTest, TestGetBulkDuplicateOidThrowsPacketError) {
   g_mode = TableShimMode::GETBULK_DUPLICATE_OID;
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   EXPECT_THROW(snmptable(args, "testing_table_bulk_dup"), PacketErrorBase);
}

TEST_F(SnmpTableWithDataShimTest, TestGetNextV1WithDebugAndShowIndex) {
   g_mode = TableShimMode::GETNEXT_NORMAL;
   std::vector<std::string> args = {
       "-d", "-Ci", "-v", "1", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   auto res = snmptable(args, "testing_table_v1_getnext");
   ASSERT_EQ(res.size(), 1u);
   EXPECT_NE(res[0].find("Name:"), std::string::npos);
   EXPECT_NE(res[0].find("Row1 Desc"), std::string::npos);
}

TEST_F(SnmpTableWithDataShimTest, TestGetNextMultiPassWithCr1) {
   g_mode = TableShimMode::GETNEXT_MULTI_PASS;
   std::vector<std::string> args = {
       "-CB", "-Cr", "1", "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   auto res = snmptable(args, "testing_table_getnext_multipass");
   ASSERT_EQ(res.size(), 1u);
   EXPECT_NE(res[0].find("Row1"), std::string::npos);
   EXPECT_NE(res[0].find("Row2"), std::string::npos);
}

TEST_F(SnmpTableWithDataShimTest, TestGetNextNoSuchName) {
   g_mode = TableShimMode::GETNEXT_NOSUCHNAME;
   std::vector<std::string> args = {
       "-CB", "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   auto res = snmptable(args, "testing_table_getnext_nosuchname");
   ASSERT_EQ(res.size(), 1u);
   EXPECT_NE(res[0].find("End of MIB"), std::string::npos);
}

TEST_F(SnmpTableWithDataShimTest, TestGetNextGenErrThrowsPacketError) {
   g_mode = TableShimMode::GETNEXT_GENERR;
   std::vector<std::string> args = {
       "-CB", "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   EXPECT_THROW(snmptable(args, "testing_table_getnext_generr"), PacketErrorBase);
}

TEST_F(SnmpTableWithDataShimTest, TestGetNextTimeoutThrowsTimeoutError) {
   g_mode = TableShimMode::GETNEXT_TIMEOUT;
   std::vector<std::string> args = {
       "-CB", "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   EXPECT_THROW(snmptable(args, "testing_table_getnext_timeout"), TimeoutErrorBase);
}

TEST_F(SnmpTableWithDataShimTest, TestGetNextStatErrorThrowsException) {
   g_mode = TableShimMode::GETNEXT_STAT_ERROR;
   std::vector<std::string> args = {
       "-CB", "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   EXPECT_THROW(snmptable(args, "testing_table_getnext_staterr"), GenericErrorBase);
}

TEST_F(SnmpTableWithDataShimTest, TestInvalidVersionThrowsParseError) {
   std::vector<std::string> args = {
       "-v", "999", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysORTable"};
   EXPECT_THROW(snmptable(args, "testing_table_invalid_ver"), ParseErrorBase);
}

TEST_F(SnmpTableWithDataShimTest, TestUnknownHostThrowsConnectionError) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "nonexistent.invalid.host.example", "SNMPv2-MIB::sysORTable"};
   EXPECT_THROW(snmptable(args, "testing_table_bad_host"), GenericErrorBase);
}

TEST_F(SnmpTableWithDataShimTest, TestNumericNonMibOidThrowsParseError) {
   std::vector<std::string> args = {
       "-Ch", "-v", "2c", "-c", "public", "localhost:11161", "1.3.6.1.4.1.99999.1.1"};
   EXPECT_THROW(snmptable(args, "testing_table_numeric_oid"), ParseErrorBase);
}
