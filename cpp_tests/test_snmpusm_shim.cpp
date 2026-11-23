#ifndef OPENSSL_SUPPRESS_DEPRECATED
#define OPENSSL_SUPPRESS_DEPRECATED
#endif
#if !defined(_WIN32) && !defined(_GNU_SOURCE)
#define _GNU_SOURCE
#endif

#include <gtest/gtest.h>
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
#include <openssl/bn.h>
#include <openssl/dh.h>

#if !defined(_WIN32)
#include <dlfcn.h>
#endif

#include <cstring>
#include <string>
#include <vector>

#include "exceptionsbase.h"
#include "snmpusm.h"
#include "test_snmp_response_helpers.h"

namespace {

enum class DhGetMode {
   kSuccess,
   kWrongType,
   kTimeout,
   kError,
   kBadDhParams,
   kNullPeerPub,
   kWrongPeerPubLen,
   kBadPrivPeerPub,
   kSmallDhParams,
   kComputeKeyFail,
};

enum class SetMode {
   kSuccess,
   kNullResponse,
   kPacketErrorNoIndex,
   kPacketErrorWithIndex,
   kTimeout,
   kError,
};

DhGetMode g_dh_get_mode = DhGetMode::kSuccess;
SetMode g_set_mode = SetMode::kSuccess;
#if !defined(_WIN32)
int g_fail_pdu_create_type = -1;
bool g_fail_pdu_get_after_set = false;
int g_fail_dh_size_on_call = 0;
int g_dh_size_call_count = 0;
bool g_fail_default_authtype = false;
int g_fail_generate_ku_on_call = 0;
int g_generate_ku_call_count = 0;
int g_fail_extend_kul_on_call = 0;
int g_extend_kul_call_count = 0;
bool g_fail_parse_args = false;
bool g_in_snmp_parse_args = false;
#endif

void add_octet_var(
    netsnmp_pdu *pdu, oid const *name, size_t name_len, u_char const *data, size_t data_len) {
   snmp_varlist_add_variable(&pdu->variables, name, name_len, ASN_OCTET_STR, data, data_len);
}

netsnmp_pdu *make_dh_get_response(DhGetMode mode) {
   netsnmp_pdu *resp = snmp_pdu_create(SNMP_MSG_RESPONSE);
   resp->errstat = SNMP_ERR_NOERROR;
   resp->errindex = 0;

   oid dh_params_oid[] = {1, 3, 6, 1, 3, 101, 1, 1, 1, 0};
   oid dh_auth_oid[] = {1, 3, 6, 1, 3, 101, 1, 1, 2, 1, 1, 1};
   oid dh_priv_oid[] = {1, 3, 6, 1, 3, 101, 1, 1, 2, 1, 3, 1};

   if (mode == DhGetMode::kWrongType) {
      snmp_add_null_var(resp, dh_params_oid, OID_LENGTH(dh_params_oid));
      return resp;
   }

   if (mode == DhGetMode::kBadDhParams) {
      u_char garbage[] = {0x01, 0x02, 0x03, 0x04};
      add_octet_var(resp, dh_params_oid, OID_LENGTH(dh_params_oid), garbage, sizeof(garbage));
      add_octet_var(resp, dh_auth_oid, OID_LENGTH(dh_auth_oid), garbage, sizeof(garbage));
      return resp;
   }

   if (mode == DhGetMode::kSmallDhParams) {
      // 32-byte (256-bit) safe prime (< outkey_len of 64 for SHA-512) to hit key_len < outkey_len
      DH *small_dh = DH_new();
      u_char p_bytes[32] = {0xCD, 0x98, 0xF5, 0x44, 0x7B, 0xE7, 0x69, 0xB3, 0x6D, 0xF1, 0x52,
                            0x4B, 0x5F, 0x88, 0x9F, 0x71, 0xC2, 0xFA, 0x1E, 0xF6, 0xFB, 0x74,
                            0xCD, 0x60, 0x80, 0xAB, 0xA1, 0x40, 0x28, 0xCF, 0x3D, 0x9F};
      u_char g_bytes[1] = {0x02};
      DH_set0_pqg(small_dh, BN_bin2bn(p_bytes, sizeof(p_bytes), nullptr), nullptr,
                  BN_bin2bn(g_bytes, sizeof(g_bytes), nullptr));
      unsigned char *der_buf = nullptr;
      int der_len = i2d_DHparams(small_dh, &der_buf);
      add_octet_var(resp, dh_params_oid, OID_LENGTH(dh_params_oid), der_buf,
                    static_cast<size_t>(der_len));
      OPENSSL_free(der_buf);
      DH_free(small_dh);
      u_char peer_pub[32] = {0x02};
      add_octet_var(resp, dh_auth_oid, OID_LENGTH(dh_auth_oid), peer_pub, sizeof(peer_pub));
      return resp;
   }

   DH *server_dh = DH_get_2048_256();
   unsigned char *der_buf = nullptr;
   int der_len = i2d_DHparams(server_dh, &der_buf);
   add_octet_var(resp, dh_params_oid, OID_LENGTH(dh_params_oid), der_buf,
                 static_cast<size_t>(der_len));
   OPENSSL_free(der_buf);

   DH_generate_key(server_dh);
   BIGNUM const *pub_key = nullptr;
   DH_get0_key(server_dh, &pub_key, nullptr);
   int dh_bytes = DH_size(server_dh);
   std::vector<u_char> pub_buf(static_cast<size_t>(dh_bytes), 0);
   int pub_len = BN_num_bytes(pub_key);
   BN_bn2bin(pub_key, pub_buf.data() + (dh_bytes - pub_len));
   DH_free(server_dh);

   if (mode == DhGetMode::kNullPeerPub) {
      // Omit dh_auth_oid so vars == nullptr in get_USM_DH_key
      return resp;
   }

   if (mode == DhGetMode::kWrongPeerPubLen) {
      u_char short_pub[10] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
      add_octet_var(resp, dh_auth_oid, OID_LENGTH(dh_auth_oid), short_pub, sizeof(short_pub));
      return resp;
   }

   if (mode == DhGetMode::kBadPrivPeerPub) {
      snmp_add_null_var(resp, dh_priv_oid, OID_LENGTH(dh_priv_oid));
      return resp;
   }

   if (mode == DhGetMode::kComputeKeyFail) {
      // Peer public key = 1 causes DH_compute_key() to return -1 (< outkey_len)
      std::vector<u_char> invalid_pub(static_cast<size_t>(dh_bytes), 0);
      invalid_pub.back() = 0x01;
      add_octet_var(resp, dh_auth_oid, OID_LENGTH(dh_auth_oid), invalid_pub.data(),
                    invalid_pub.size());
      add_octet_var(resp, dh_priv_oid, OID_LENGTH(dh_priv_oid), invalid_pub.data(),
                    invalid_pub.size());
      return resp;
   }

   add_octet_var(resp, dh_auth_oid, OID_LENGTH(dh_auth_oid), pub_buf.data(), pub_buf.size());
   add_octet_var(resp, dh_priv_oid, OID_LENGTH(dh_priv_oid), pub_buf.data(), pub_buf.size());
   return resp;
}

} // namespace

extern "C" int snmp_sess_synch_response(ezsnmp_test::session_handle sessp,
                                        netsnmp_pdu *pdu,
                                        netsnmp_pdu **response) {
   (void)sessp;

   if (pdu != nullptr && pdu->command == SNMP_MSG_GET) {
      if (pdu != nullptr) {
         snmp_free_pdu(pdu);
      }
      switch (g_dh_get_mode) {
         case DhGetMode::kTimeout:
            *response = nullptr;
            return STAT_TIMEOUT;
         case DhGetMode::kError:
            *response = nullptr;
            return STAT_ERROR;
         default:
            *response = make_dh_get_response(g_dh_get_mode);
            return STAT_SUCCESS;
      }
   }

   if (pdu != nullptr) {
      snmp_free_pdu(pdu);
   }

   switch (g_set_mode) {
      case SetMode::kNullResponse:
         *response = nullptr;
         return STAT_SUCCESS;
      case SetMode::kPacketErrorNoIndex: {
         netsnmp_pdu *resp = snmp_pdu_create(SNMP_MSG_RESPONSE);
         resp->errstat = SNMP_ERR_GENERR;
         resp->errindex = 0;
         *response = resp;
         return STAT_SUCCESS;
      }
      case SetMode::kPacketErrorWithIndex: {
         netsnmp_pdu *resp = snmp_pdu_create(SNMP_MSG_RESPONSE);
         resp->errstat = SNMP_ERR_GENERR;
         resp->errindex = 2;
         oid o1[] = {1, 3, 6, 1, 2, 1, 1, 5, 0};
         oid o2[] = {1, 3, 6, 1, 2, 1, 1, 6, 0};
         long v = 1;
         snmp_varlist_add_variable(&resp->variables, o1, OID_LENGTH(o1), ASN_INTEGER,
                                   reinterpret_cast<u_char *>(&v), sizeof(v));
         snmp_varlist_add_variable(&resp->variables, o2, OID_LENGTH(o2), ASN_INTEGER,
                                   reinterpret_cast<u_char *>(&v), sizeof(v));
         *response = resp;
         return STAT_SUCCESS;
      }
      case SetMode::kTimeout:
         *response = nullptr;
         return STAT_TIMEOUT;
      case SetMode::kError:
         *response = nullptr;
         return STAT_ERROR;
      case SetMode::kSuccess:
      default: {
         netsnmp_pdu *resp = snmp_pdu_create(SNMP_MSG_RESPONSE);
         resp->errstat = SNMP_ERR_NOERROR;
         resp->errindex = 0;
         *response = resp;
         return STAT_SUCCESS;
      }
   }
}

class SnmpUsmShimTest : public ::testing::Test {
  protected:
   void SetUp() override {
      g_dh_get_mode = DhGetMode::kSuccess;
      g_set_mode = SetMode::kSuccess;
   }
};

TEST_F(SnmpUsmShimTest, TestCreateCloneDeleteActivateDeactivateAndOptions) {
   std::vector<std::string> base = {"-v", "2c", "-c",   "public",         "-r",
                                    "0",  "-t", "0.05", "localhost:11161"};

   // create with cloneFrom
   auto args = base;
   args.insert(args.end(), {"create", "u1", "u0"});
   EXPECT_EQ(snmpusm(args, "shim"), std::vector<std::string>({"User successfully created."}));

   // create with -Cw and cloneFrom
   args = {"-Cw",    "-v", "2c", "-c", "public", "-r", "0", "-t", "0.05", "localhost:11161",
           "create", "u1", "u0"};
   EXPECT_EQ(snmpusm(args, "shim"), std::vector<std::string>({"User successfully created."}));

   // create without cloneFrom (RS_CREATEANDWAIT)
   args = base;
   args.insert(args.end(), {"create", "u1"});
   EXPECT_EQ(snmpusm(args, "shim"), std::vector<std::string>({"User successfully created."}));

   // cloneFrom
   args = base;
   args.insert(args.end(), {"cloneFrom", "u1", "u0"});
   EXPECT_EQ(snmpusm(args, "shim"), std::vector<std::string>({"User successfully cloned."}));

   // delete, activate, deactivate
   args = base;
   args.insert(args.end(), {"delete", "u1"});
   EXPECT_EQ(snmpusm(args, "shim"), std::vector<std::string>({"User successfully deleted."}));

   args = base;
   args.insert(args.end(), {"activate", "u1"});
   EXPECT_EQ(snmpusm(args, "shim"), std::vector<std::string>({"User successfully activated."}));

   args = base;
   args.insert(args.end(), {"deactivate", "u1"});
   EXPECT_EQ(snmpusm(args, "shim"), std::vector<std::string>({"User successfully deactivated."}));

   // -CE repeated (tests freeing previously allocated usmUserEngineID) + -Cp with v3 user
   args = {"-CE",
           "800000020109840301",
           "-CE",
           "800000020109840302",
           "-Cp",
           "pubval",
           "-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_md5_aes",
           "-l",
           "authPriv",
           "-a",
           "MD5",
           "-A",
           "auth_pass",
           "-x",
           "AES",
           "-X",
           "priv_pass",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "activate",
           "u1"};
   EXPECT_EQ(snmpusm(args, "shim"), std::vector<std::string>({"User successfully activated."}));
}

TEST_F(SnmpUsmShimTest, TestCpWithoutSecurityNameThrows) {
   std::vector<std::string> args = {
       "-Cp",  "pubval",          "-v",       "2c", "-c", "public", "-r", "0", "-t",
       "0.05", "localhost:11161", "activate", "u1"};
   EXPECT_THROW(snmpusm(args, "shim"), ParseErrorBase);
}

TEST_F(SnmpUsmShimTest, TestOidExceedsMaxLenThrows) {
   std::string long_user(130, 'a');
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-r", "0", "-t", "0.05", "localhost:11161", "delete", long_user};
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);
}

TEST_F(SnmpUsmShimTest, TestPasswdVariantsAndErrors) {
   // Own key (no user arg), MD5 + AES
   std::vector<std::string> args = {"-v",
                                    "3",
                                    "-e",
                                    "800000020109840301",
                                    "-E",
                                    "800000020109840301",
                                    "-u",
                                    "initial_md5_aes",
                                    "-l",
                                    "authPriv",
                                    "-a",
                                    "MD5",
                                    "-A",
                                    "auth_pass",
                                    "-x",
                                    "AES",
                                    "-X",
                                    "priv_pass",
                                    "-r",
                                    "0",
                                    "-t",
                                    "0.05",
                                    "localhost:11161",
                                    "passwd",
                                    "oldpass123",
                                    "newpass123"};
   EXPECT_EQ(snmpusm(args, "shim"),
             std::vector<std::string>({"SNMPv3 Key(s) successfully changed."}));

   // -Ca only with target user
   args = {"-Ca",
           "-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_md5_aes",
           "-l",
           "authPriv",
           "-a",
           "MD5",
           "-A",
           "auth_pass",
           "-x",
           "AES",
           "-X",
           "priv_pass",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "passwd",
           "oldpass123",
           "newpass123",
           "targetu"};
   EXPECT_EQ(snmpusm(args, "shim"),
             std::vector<std::string>({"SNMPv3 Key(s) successfully changed."}));

   // -Cx only with target user
   args[0] = "-Cx";
   EXPECT_EQ(snmpusm(args, "shim"),
             std::vector<std::string>({"SNMPv3 Key(s) successfully changed."}));

   // -Ck localized keys (valid hex)
   args = {"-Ck",
           "-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_md5_aes",
           "-l",
           "authPriv",
           "-a",
           "MD5",
           "-A",
           "auth_pass",
           "-x",
           "AES",
           "-X",
           "priv_pass",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "passwd",
           "0x0123456789abcdef0123456789abcdef",
           "0xfedcba9876543210fedcba9876543210",
           "targetu"};
   EXPECT_EQ(snmpusm(args, "shim"),
             std::vector<std::string>({"SNMPv3 Key(s) successfully changed."}));

   // -Ck bad old hex
   args[25] = "0xZZZZZZZZZZZZZZ";
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);

   // -Ck bad new hex
   args[25] = "0x0123456789abcdef0123456789abcdef";
   args[26] = "0xZZZZZZZZZZZZZZ";
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);

   // SHA + AES128 (oldkulpriv_len > properlength truncation branch)
   args = {"-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "secondary_sha_aes",
           "-l",
           "authPriv",
           "-a",
           "SHA",
           "-A",
           "auth_second",
           "-x",
           "AES",
           "-X",
           "priv_second",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "passwd",
           "oldpass123",
           "newpass123"};
   EXPECT_EQ(snmpusm(args, "shim"),
             std::vector<std::string>({"SNMPv3 Key(s) successfully changed."}));

   // -Ck with short 8-byte localized key + MD5 + AES (oldkulpriv_len < properlength ->
   // netsnmp_extend_kul)
   args = {"-Ck",
           "-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_md5_aes",
           "-l",
           "authPriv",
           "-a",
           "MD5",
           "-A",
           "auth_pass",
           "-x",
           "AES",
           "-X",
           "priv_pass",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "passwd",
           "0x0123456789abcdef",
           "0xfedcba9876543210",
           "targetu"};
   EXPECT_EQ(snmpusm(args, "shim"),
             std::vector<std::string>({"SNMPv3 Key(s) successfully changed."}));

   // No securityName (v2c)
   args = {"-v",         "2c",        "-c",   "public",          "-r",
           "0",          "-t",        "0.05", "localhost:11161", "passwd",
           "oldpass123", "newpass123"};
   EXPECT_THROW(snmpusm(args, "shim"), ParseErrorBase);

   // No priv proto (authNoPriv)
   args = {"-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_md5_no_priv",
           "-l",
           "authNoPriv",
           "-a",
           "MD5",
           "-A",
           "auth_pass",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "passwd",
           "oldpass123",
           "newpass123"};
   EXPECT_THROW(snmpusm(args, "shim"), ParseErrorBase);

   // No auth proto (noAuthNoPriv) -> hits default auth proto branch before priv proto check
   args = {"-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_md5_no_priv",
           "-l",
           "noAuthNoPriv",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "passwd",
           "oldpass123",
           "newpass123"};
   EXPECT_THROW(snmpusm(args, "shim"), ParseErrorBase);

   // MD5 + DES (hits USM_CREATE_USER_PRIV_DES branch)
   args = {"-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_md5_des",
           "-l",
           "authPriv",
           "-a",
           "MD5",
           "-A",
           "auth_pass",
           "-x",
           "DES",
           "-X",
           "priv_pass",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "passwd",
           "oldpass123",
           "newpass123"};
   EXPECT_EQ(snmpusm(args, "shim"),
             std::vector<std::string>({"SNMPv3 Key(s) successfully changed."}));

   // Empty oldpass -> generate_Ku fails for old Ku
   args = {"-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_md5_aes",
           "-l",
           "authPriv",
           "-a",
           "MD5",
           "-A",
           "auth_pass",
           "-x",
           "AES",
           "-X",
           "priv_pass",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "passwd",
           "",
           "newpass123"};
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);

   // Empty newpass -> generate_Ku fails for new Ku
   args = {"-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_md5_aes",
           "-l",
           "authPriv",
           "-a",
           "MD5",
           "-A",
           "auth_pass",
           "-x",
           "AES",
           "-X",
           "priv_pass",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "passwd",
           "oldpass123",
           ""};
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);

   // -Ck with mismatched localized key lengths -> encode_keychange fails for auth and priv
   args = {"-Ca",
           "-Ck",
           "-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_md5_aes",
           "-l",
           "authPriv",
           "-a",
           "MD5",
           "-A",
           "auth_pass",
           "-x",
           "AES",
           "-X",
           "priv_pass",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "passwd",
           "0x1234",
           "0x56789abc"};
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);

   args[0] = "-Cx";
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);

   // -Ca -Ck with mismatched key lengths (16-byte old vs 8-byte new) triggers
   // encode_keychange failure (auth)
   args = {"-Ca",
           "-Ck",
           "-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_md5_aes",
           "-l",
           "authPriv",
           "-a",
           "MD5",
           "-A",
           "auth_pass",
           "-x",
           "AES",
           "-X",
           "priv_pass",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "passwd",
           "0x0123456789abcdef0123456789abcdef",
           "0x0123456789abcdef",
           "targetu"};
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);

   // -Cx -Ck with mismatched priv key lengths (16-byte old vs 8-byte new) triggers
   // encode_keychange failure (priv)
   args[0] = "-Cx";
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);
}

TEST_F(SnmpUsmShimTest, TestChangekeySuccessAndErrors) {
   // Default (-Ca and -Cx) with user; retry once if random DH pubkey has leading zero byte
   std::vector<std::string> args = {"-v",
                                    "3",
                                    "-e",
                                    "800000020109840301",
                                    "-E",
                                    "800000020109840301",
                                    "-u",
                                    "initial_md5_aes",
                                    "-l",
                                    "authPriv",
                                    "-a",
                                    "MD5",
                                    "-A",
                                    "auth_pass",
                                    "-x",
                                    "AES",
                                    "-X",
                                    "priv_pass",
                                    "-r",
                                    "0",
                                    "-t",
                                    "0.05",
                                    "localhost:11161",
                                    "changekey",
                                    "targetu"};
   std::vector<std::string> res;
   for (int attempt = 0; attempt < 3; ++attempt) {
      try {
         res = snmpusm(args, "shim");
         break;
      } catch (GenericErrorBase const &e) {
         if (std::string(e.what()).find("incorrect diffie-helman lengths") == std::string::npos ||
             attempt == 2) {
            throw;
         }
      }
   }
   ASSERT_EQ(res.size(), 3u);
   EXPECT_TRUE(res[0].find("new auth key: 0x") != std::string::npos);
   EXPECT_TRUE(res[1].find("new priv key: 0x") != std::string::npos);
   EXPECT_EQ(res[2], "SNMPv3 Key(s) successfully changed.");

   // -Ca only (own key)
   args = {"-Ca",
           "-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_md5_aes",
           "-l",
           "authPriv",
           "-a",
           "MD5",
           "-A",
           "auth_pass",
           "-x",
           "AES",
           "-X",
           "priv_pass",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "changekey"};
   for (int attempt = 0; attempt < 3; ++attempt) {
      try {
         res = snmpusm(args, "shim");
         break;
      } catch (GenericErrorBase const &e) {
         if (std::string(e.what()).find("incorrect diffie-helman lengths") == std::string::npos ||
             attempt == 2) {
            throw;
         }
      }
   }
   ASSERT_EQ(res.size(), 2u);
   EXPECT_TRUE(res[0].find("new auth key: 0x") != std::string::npos);

   // -Cx only (own key)
   args[0] = "-Cx";
   for (int attempt = 0; attempt < 3; ++attempt) {
      try {
         res = snmpusm(args, "shim");
         break;
      } catch (GenericErrorBase const &e) {
         if (std::string(e.what()).find("incorrect diffie-helman lengths") == std::string::npos ||
             attempt == 2) {
            throw;
         }
      }
   }
   ASSERT_EQ(res.size(), 2u);
   EXPECT_TRUE(res[0].find("new priv key: 0x") != std::string::npos);

   // No securityName
   args = {"-v", "2c", "-c", "public", "-r", "0", "-t", "0.05", "localhost:11161", "changekey"};
   EXPECT_THROW(snmpusm(args, "shim"), ParseErrorBase);

   // DH GET wrong variable type
   args = {"-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_md5_aes",
           "-l",
           "authPriv",
           "-a",
           "MD5",
           "-A",
           "auth_pass",
           "-x",
           "AES",
           "-X",
           "priv_pass",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "changekey",
           "targetu"};
   g_dh_get_mode = DhGetMode::kWrongType;
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);

   // DH GET timeout
   g_dh_get_mode = DhGetMode::kTimeout;
   EXPECT_THROW(snmpusm(args, "shim"), TimeoutErrorBase);

   // DH GET error
   g_dh_get_mode = DhGetMode::kError;
   EXPECT_ANY_THROW(snmpusm(args, "shim"));

   // Bad DH params
   g_dh_get_mode = DhGetMode::kBadDhParams;
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);

   // Null peer pubkey (auth)
   g_dh_get_mode = DhGetMode::kNullPeerPub;
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);

   // Wrong peer pubkey len
   g_dh_get_mode = DhGetMode::kWrongPeerPubLen;
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);

   // Null peer pubkey (priv only)
   g_dh_get_mode = DhGetMode::kBadPrivPeerPub;
   args = {"-Cx",
           "-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_md5_aes",
           "-l",
           "authPriv",
           "-a",
           "MD5",
           "-A",
           "auth_pass",
           "-x",
           "AES",
           "-X",
           "priv_pass",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "changekey",
           "targetu"};
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);

   // Small DH params
   g_dh_get_mode = DhGetMode::kSmallDhParams;
   args = {"-Cx",
           "-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_sha512_aes",
           "-l",
           "authPriv",
           "-a",
           "SHA-512",
           "-A",
           "auth_pass",
           "-x",
           "AES",
           "-X",
           "priv_pass",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "changekey",
           "targetu"};
   for (int attempt = 0; attempt < 8; ++attempt) {
      try {
         snmpusm(args, "shim");
         FAIL() << "Expected GenericErrorBase";
      } catch (GenericErrorBase const &e) {
         if (std::string(e.what()).find("Failed to compute Diffie-Hellman") != std::string::npos) {
            break;
         }
         if (attempt == 7) {
            throw;
         }
      }
   }

   // DH_compute_key failure (computed_len < outkey_len)
   g_dh_get_mode = DhGetMode::kComputeKeyFail;
   for (int attempt = 0; attempt < 3; ++attempt) {
      try {
         snmpusm(args, "shim");
         FAIL() << "Expected GenericErrorBase";
      } catch (GenericErrorBase const &e) {
         if (std::string(e.what()).find("Failed to compute Diffie-Hellman") != std::string::npos) {
            break;
         }
         if (attempt == 2) {
            throw;
         }
      }
   }

   // Default secname from NETSNMP_DS_LIB_SECNAME for changekey and -Cp
   netsnmp_ds_set_string(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_SECNAME, "initial_md5_aes");
   g_dh_get_mode = DhGetMode::kWrongType;
   args = {"-Cp",  "pubval",          "-v",       "2c", "-c", "public", "-r", "0", "-t",
           "0.05", "localhost:11161", "changekey"};
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);

   // Default secname from NETSNMP_DS_LIB_SECNAME for passwd (v2c has empty engineID -> generate_kul
   // fails)
   args = {"-v",         "2c",        "-c",   "public",          "-r",
           "0",          "-t",        "0.05", "localhost:11161", "passwd",
           "oldpass123", "newpass123"};
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);

   // -Ck oldpass succeeds via hex, newpass fails generate_kul due to empty engineID
   args = {"-Ck",       "-v",
           "2c",        "-c",
           "public",    "-r",
           "0",         "-t",
           "0.05",      "localhost:11161",
           "passwd",    "0x0123456789abcdef0123456789abcdef",
           "newpass123"};
   EXPECT_THROW(snmpusm(args, "shim"), GenericErrorBase);

   // -Cp with default secname from NETSNMP_DS_LIB_SECNAME on delete (session.securityName ==
   // nullptr)
   args = {"-Cp",  "pubval",          "-v",     "2c", "-c", "public", "-r", "0", "-t",
           "0.05", "localhost:11161", "delete", "u1"};
   EXPECT_EQ(snmpusm(args, "shim"), std::vector<std::string>({"User successfully deleted."}));
   netsnmp_ds_set_string(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_SECNAME, nullptr);

   // DES changekey (hits USM_CREATE_USER_PRIV_DES in changekey)
   g_dh_get_mode = DhGetMode::kSuccess;
   args = {"-Cx",
           "-v",
           "3",
           "-e",
           "800000020109840301",
           "-E",
           "800000020109840301",
           "-u",
           "initial_md5_des",
           "-l",
           "authPriv",
           "-a",
           "MD5",
           "-A",
           "auth_pass",
           "-x",
           "DES",
           "-X",
           "priv_pass",
           "-r",
           "0",
           "-t",
           "0.05",
           "localhost:11161",
           "changekey",
           "targetu"};
   for (int attempt = 0; attempt < 3; ++attempt) {
      try {
         res = snmpusm(args, "shim");
         break;
      } catch (GenericErrorBase const &e) {
         if (std::string(e.what()).find("incorrect diffie-helman lengths") == std::string::npos ||
             attempt == 2) {
            throw;
         }
      }
   }
   ASSERT_EQ(res.size(), 2u);
}

TEST_F(SnmpUsmShimTest, TestFinalResponseErrorPaths) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "-r", "0", "-t", "0.05", "localhost:11161", "delete", "u1"};

   g_set_mode = SetMode::kNullResponse;
   EXPECT_THROW(snmpusm(args, "shim"), PacketErrorBase);

   g_set_mode = SetMode::kPacketErrorNoIndex;
   EXPECT_THROW(snmpusm(args, "shim"), PacketErrorBase);

   g_set_mode = SetMode::kPacketErrorWithIndex;
   EXPECT_THROW(snmpusm(args, "shim"), PacketErrorBase);

   g_set_mode = SetMode::kTimeout;
   EXPECT_THROW(snmpusm(args, "shim"), TimeoutErrorBase);

   g_set_mode = SetMode::kError;
   EXPECT_ANY_THROW(snmpusm(args, "shim"));
}

TEST_F(SnmpUsmShimTest, TestSessOpenFailureThrows) {
   std::vector<std::string> args = {
       "-v", "2c", "-c", "public", "nonexistent_host_for_usm_test:11161", "delete", "u1"};
   EXPECT_THROW(snmpusm(args, "shim"), ConnectionErrorBase);
}

TEST_F(SnmpUsmShimTest, TestParseArgsErrorThrows) {
   std::vector<std::string> args = {"-v", "3", "-e", "ZZZZ", "localhost:11161", "delete", "u1"};
   EXPECT_THROW(snmpusm(args, "shim"), ParseErrorBase);

   args = {"-v", "99", "localhost:11161", "delete", "u1"};
   EXPECT_THROW(snmpusm(args, "shim"), ParseErrorBase);

   args = {"-v", "3", "-a", "INVALID", "localhost:11161", "delete", "u1"};
   EXPECT_THROW(snmpusm(args, "shim"), ParseErrorBase);

   args = {"-v", "3", "-Z", "bad", "localhost:11161", "delete", "u1"};
   EXPECT_THROW(snmpusm(args, "shim"), ParseErrorBase);

   args = {"-v", "3", "-3k", "ZZZZ", "localhost:11161", "delete", "u1"};
   EXPECT_THROW(snmpusm(args, "shim"), ParseErrorBase);
}

#if !defined(_WIN32)
extern "C" netsnmp_pdu *snmp_pdu_create(int type) {
   using fn_t = netsnmp_pdu *(*)(int);
   static fn_t real_fn = reinterpret_cast<fn_t>(dlsym(RTLD_NEXT, "snmp_pdu_create"));
   if (type == g_fail_pdu_create_type) {
      return nullptr;
   }
   if (g_fail_pdu_get_after_set && type == SNMP_MSG_SET) {
      g_fail_pdu_create_type = SNMP_MSG_GET;
      g_fail_pdu_get_after_set = false;
   }
   if (real_fn == nullptr) {
      return nullptr;
   }
   return real_fn(type);
}

extern "C" int DH_size(DH const *dh) {
   using fn_t = int (*)(DH const *);
   static fn_t real_fn = reinterpret_cast<fn_t>(dlsym(RTLD_NEXT, "DH_size"));
   ++g_dh_size_call_count;
   if (g_fail_dh_size_on_call > 0 && g_dh_size_call_count == g_fail_dh_size_on_call) {
      return 0;
   }
   if (real_fn == nullptr) {
      return 0;
   }
   return real_fn(dh);
}

extern "C" oid const *get_default_authtype(size_t *len) {
   using fn_t = oid const *(*)(size_t *);
   static fn_t real_fn = reinterpret_cast<fn_t>(dlsym(RTLD_NEXT, "get_default_authtype"));
   if (g_fail_default_authtype || real_fn == nullptr) {
      if (len != nullptr) {
         *len = 0;
      }
      return nullptr;
   }
   return real_fn(len);
}

extern "C" int generate_Ku(oid const *hashtype,
                           u_int hashtype_len,
                           u_char const *P,
                           size_t pplen,
                           u_char *Ku,
                           size_t *kulen) {
   using fn_t = int (*)(oid const *, u_int, u_char const *, size_t, u_char *, size_t *);
   static fn_t real_fn = reinterpret_cast<fn_t>(dlsym(RTLD_NEXT, "generate_Ku"));
   if (!g_in_snmp_parse_args) {
      ++g_generate_ku_call_count;
      if (g_fail_generate_ku_on_call > 0 &&
          g_generate_ku_call_count == g_fail_generate_ku_on_call) {
         return SNMPERR_GENERR;
      }
   }
   if (real_fn == nullptr) {
      return SNMPERR_GENERR;
   }
   return real_fn(hashtype, hashtype_len, P, pplen, Ku, kulen);
}

extern "C" int netsnmp_extend_kul(u_int needKeyLen,
                                  oid *hashoid,
                                  u_int hashoid_len,
                                  int privType,
                                  u_char *engineID,
                                  u_int engineIDLen,
                                  u_char **kulBuf,
                                  size_t *kulBufLen,
                                  u_int kulBufSize) {
   using fn_t = int (*)(u_int, oid *, u_int, int, u_char *, u_int, u_char **, size_t *, u_int);
   static fn_t real_fn = reinterpret_cast<fn_t>(dlsym(RTLD_NEXT, "netsnmp_extend_kul"));
   ++g_extend_kul_call_count;
   if (g_fail_extend_kul_on_call > 0 && g_extend_kul_call_count == g_fail_extend_kul_on_call) {
      return SNMPERR_GENERR;
   }
   if (real_fn == nullptr) {
      return SNMPERR_SUCCESS;
   }
   return real_fn(needKeyLen, hashoid, hashoid_len, privType, engineID, engineIDLen, kulBuf,
                  kulBufLen, kulBufSize);
}

extern "C" int snmp_parse_args(int argc,
                               char **argv,
                               netsnmp_session *session,
                               char const *localOpts,
                               void (*proc)(int, char *const *, int)) {
   using fn_t =
       int (*)(int, char **, netsnmp_session *, char const *, void (*)(int, char *const *, int));
   static fn_t real_fn = reinterpret_cast<fn_t>(dlsym(RTLD_NEXT, "snmp_parse_args"));
   if (g_fail_parse_args || real_fn == nullptr) {
      return NETSNMP_PARSE_ARGS_ERROR;
   }
   struct ParseArgsScope {
      ParseArgsScope() { g_in_snmp_parse_args = true; }
      ~ParseArgsScope() { g_in_snmp_parse_args = false; }
   } scope;
   return real_fn(argc, argv, session, localOpts, proc);
}

TEST_F(SnmpUsmShimTest, TestFaultInjectionParseArgsErrorThrows) {
   struct Guard {
      ~Guard() { g_fail_parse_args = false; }
   } guard;

   g_fail_parse_args = true;
   EXPECT_THROW(snmpusm({"-v", "2c", "-c", "public", "localhost:11161", "delete", "u1"}, "shim"),
                ParseErrorBase);
}

TEST_F(SnmpUsmShimTest, TestFaultInjectionPduCreateSetFailureThrows) {
   struct Guard {
      ~Guard() { g_fail_pdu_create_type = -1; }
   } guard;

   g_fail_pdu_create_type = SNMP_MSG_SET;
   EXPECT_THROW(snmpusm({"-v", "2c", "-c", "public", "-r", "0", "-t", "0.05", "localhost:11161",
                         "delete", "u1"},
                        "shim"),
                GenericErrorBase);
}

TEST_F(SnmpUsmShimTest, TestFaultInjectionPduCreateGetFailureInChangekeyThrows) {
   struct Guard {
      ~Guard() {
         g_fail_pdu_create_type = -1;
         g_fail_pdu_get_after_set = false;
      }
   } guard;

   g_fail_pdu_get_after_set = true;
   std::vector<std::string> ck_args = {"-Ca",
                                       "-v",
                                       "3",
                                       "-e",
                                       "800000020109840301",
                                       "-E",
                                       "800000020109840301",
                                       "-u",
                                       "initial_md5_aes",
                                       "-l",
                                       "authPriv",
                                       "-a",
                                       "MD5",
                                       "-A",
                                       "auth_pass",
                                       "-x",
                                       "AES",
                                       "-X",
                                       "priv_pass",
                                       "-r",
                                       "0",
                                       "-t",
                                       "0.05",
                                       "localhost:11161",
                                       "changekey",
                                       "targetu"};
   EXPECT_THROW(snmpusm(ck_args, "shim"), GenericErrorBase);
}

TEST_F(SnmpUsmShimTest, TestFaultInjectionDhSizeZeroThrows) {
   struct Guard {
      ~Guard() {
         g_fail_dh_size_on_call = 0;
         g_dh_size_call_count = 0;
         g_dh_get_mode = DhGetMode::kSuccess;
      }
   } guard;

   std::vector<std::string> ck_args = {"-Ca",
                                       "-v",
                                       "3",
                                       "-e",
                                       "800000020109840301",
                                       "-E",
                                       "800000020109840301",
                                       "-u",
                                       "initial_md5_aes",
                                       "-l",
                                       "authPriv",
                                       "-a",
                                       "MD5",
                                       "-A",
                                       "auth_pass",
                                       "-x",
                                       "AES",
                                       "-X",
                                       "priv_pass",
                                       "-r",
                                       "0",
                                       "-t",
                                       "0.05",
                                       "localhost:11161",
                                       "changekey",
                                       "targetu"};
   g_dh_get_mode = DhGetMode::kSuccess;
   for (int attempt = 0; attempt < 3; ++attempt) {
      g_dh_size_call_count = 0;
      g_fail_dh_size_on_call = 2;
      try {
         snmpusm(ck_args, "shim");
         FAIL() << "Expected GenericErrorBase";
      } catch (GenericErrorBase const &e) {
         if (std::string(e.what()).find("Failed to compute Diffie-Hellman") != std::string::npos) {
            break;
         }
         if (attempt == 2) {
            throw;
         }
      }
   }
}

TEST_F(SnmpUsmShimTest, TestFaultInjectionDefaultAuthTypeNullThrows) {
   struct Guard {
      ~Guard() { g_fail_default_authtype = false; }
   } guard;

   g_fail_default_authtype = true;
   std::vector<std::string> pw_args = {
       "-v",     "2c",         "-c",         "public", "-r", "0", "-t", "0.05", "localhost:11161",
       "passwd", "oldpass123", "newpass123", "targetu"};
   // Will fail at generate_kul due to empty v2c engineID, after exercising lines 596-604
   EXPECT_THROW(snmpusm(pw_args, "shim"), GenericErrorBase);
}

TEST_F(SnmpUsmShimTest, TestFaultInjectionGenerateKuFailureThrows) {
   struct Guard {
      ~Guard() {
         g_fail_generate_ku_on_call = 0;
         g_generate_ku_call_count = 0;
         g_in_snmp_parse_args = false;
      }
   } guard;

   std::vector<std::string> v3_pw_args = {"-v",
                                          "3",
                                          "-e",
                                          "800000020109840301",
                                          "-E",
                                          "800000020109840301",
                                          "-u",
                                          "initial_md5_aes",
                                          "-l",
                                          "authPriv",
                                          "-a",
                                          "MD5",
                                          "-A",
                                          "auth_pass",
                                          "-x",
                                          "AES",
                                          "-X",
                                          "priv_pass",
                                          "-r",
                                          "0",
                                          "-t",
                                          "0.05",
                                          "localhost:11161",
                                          "passwd",
                                          "oldpass123",
                                          "newpass123",
                                          "targetu"};
   g_generate_ku_call_count = 0;
   g_fail_generate_ku_on_call = 1;
   EXPECT_THROW(snmpusm(v3_pw_args, "shim"), GenericErrorBase);

   g_generate_ku_call_count = 0;
   g_fail_generate_ku_on_call = 2;
   EXPECT_THROW(snmpusm(v3_pw_args, "shim"), GenericErrorBase);
}

TEST_F(SnmpUsmShimTest, TestFaultInjectionExtendKulFailureThrows) {
   struct Guard {
      ~Guard() {
         g_fail_extend_kul_on_call = 0;
         g_extend_kul_call_count = 0;
      }
   } guard;

   // Use -Ck with 8-byte key and AES (16-byte priv key) so oldkulpriv_len < properlength
   std::vector<std::string> extend_args = {"-Cx",
                                           "-Ck",
                                           "-v",
                                           "3",
                                           "-e",
                                           "800000020109840301",
                                           "-E",
                                           "800000020109840301",
                                           "-u",
                                           "initial_md5_aes",
                                           "-l",
                                           "authPriv",
                                           "-a",
                                           "MD5",
                                           "-A",
                                           "auth_pass",
                                           "-x",
                                           "AES",
                                           "-X",
                                           "priv_pass",
                                           "-r",
                                           "0",
                                           "-t",
                                           "0.05",
                                           "localhost:11161",
                                           "passwd",
                                           "0x0123456789abcdef",
                                           "0x0123456789abcdef",
                                           "targetu"};
   g_extend_kul_call_count = 0;
   g_fail_extend_kul_on_call = 1;
   EXPECT_THROW(snmpusm(extend_args, "shim"), GenericErrorBase);

   g_extend_kul_call_count = 0;
   g_fail_extend_kul_on_call = 2;
   EXPECT_THROW(snmpusm(extend_args, "shim"), GenericErrorBase);
}
#endif
