#include <gtest/gtest.h>

#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>

#include "helpers.h"

namespace {

bool g_fail_calloc = false;
bool g_fail_strdup = false;
bool g_force_sprint_variable_fail = false;
bool g_force_objid_overflow = false;

usmUser g_user1{};
usmUser g_user2{};
usmUser *g_user_list = nullptr;
int g_usm_remove_calls = 0;
int g_usm_free_calls = 0;

void reset_shim_state() {
   g_fail_calloc = false;
   g_fail_strdup = false;
   g_force_sprint_variable_fail = false;
   g_force_objid_overflow = false;

   g_user1 = usmUser{};
   g_user2 = usmUser{};
   g_user_list = nullptr;
   g_usm_remove_calls = 0;
   g_usm_free_calls = 0;
}

} // namespace

extern "C" void *calloc(size_t n, size_t size) {
   if (g_fail_calloc) {
      return nullptr;
   }

   size_t const total = n * size;
   void *ptr = std::malloc(total);
   if (ptr != nullptr) {
      std::memset(ptr, 0, total);
   }
   return ptr;
}

extern "C" char *strdup(char const *src) {
   if (g_fail_strdup) {
      return nullptr;
   }

   size_t const length = std::strlen(src) + 1;
   auto *out = static_cast<char *>(std::malloc(length));
   if (out != nullptr) {
      std::memcpy(out, src, length);
   }
   return out;
}

extern "C" int sprint_realloc_variable(u_char **buf,
                                       size_t *buf_len,
                                       size_t *out_len,
                                       int,
                                       oid const *,
                                       size_t,
                                       netsnmp_variable_list const *) {
   char const *text = g_force_sprint_variable_fail ? "partial" : "ok";
   size_t const need = std::strlen(text);

   if (buf == nullptr || *buf == nullptr || buf_len == nullptr || *buf_len <= need ||
       out_len == nullptr) {
      return 0;
   }

   std::memcpy(*buf, text, need);
   (*buf)[need] = '\0';
   *out_len = need;

   return g_force_sprint_variable_fail ? 0 : 1;
}

extern "C" struct tree *netsnmp_sprint_realloc_objid_tree(
    u_char **buf, size_t *buf_len, size_t *out_len, int, int *buf_overflow, oid const *, size_t) {
   char const *text = "obj";
   size_t const need = std::strlen(text);

   if (buf != nullptr && *buf != nullptr && buf_len != nullptr && *buf_len > need &&
       out_len != nullptr) {
      std::memcpy(*buf, text, need);
      (*buf)[need] = '\0';
      *out_len = need;
   }

   if (buf_overflow != nullptr) {
      *buf_overflow = g_force_objid_overflow ? 1 : 0;
   }

   return nullptr;
}

extern "C" usmUser *usm_get_userList(void) { return g_user_list; }

extern "C" usmUser *usm_remove_user(usmUser *user) {
   ++g_usm_remove_calls;
   return user;
}

extern "C" usmUser *usm_free_user(usmUser *user) {
   ++g_usm_free_calls;
   return user;
}

class HelpersBranchesShimTest : public ::testing::Test {
  protected:
   void SetUp() override { reset_shim_state(); }

   void TearDown() override { reset_shim_state(); }
};

TEST_F(HelpersBranchesShimTest, PrintVariableToStringCoversTruncatedAndAllocFail) {
   oid name[] = {1, 3, 6, 1};
   netsnmp_variable_list variable{};

   g_fail_calloc = true;
   EXPECT_EQ(print_variable_to_string(name, OID_LENGTH(name), &variable), "[TRUNCATED]");

   g_fail_calloc = false;
   g_force_sprint_variable_fail = true;
   EXPECT_EQ(print_variable_to_string(name, OID_LENGTH(name), &variable), "partial [TRUNCATED]");
}

TEST_F(HelpersBranchesShimTest, CreateArgvThrowsOnStrdupFailure) {
   int argc = 0;
   g_fail_strdup = true;
   EXPECT_THROW((void)create_argv({"-v2c", "-c", "public", "127.0.0.1"}, argc), std::runtime_error);
}

TEST_F(HelpersBranchesShimTest, ParseResultRegexFallbackBranch) {
   auto result = parse_result("SNMPv2-MIB::sysDescr = STRING: value");
   EXPECT_EQ(result.oid, "SNMPv2-MIB::sysDescr");
   EXPECT_EQ(result.index, "");
   EXPECT_EQ(result.type, "STRING");
   EXPECT_EQ(result.value, "value");
}

TEST_F(HelpersBranchesShimTest, ParseResultCoversOidIndexReBranch) {
   auto result = parse_result(".1.3.6.1.2.1. = INTEGER: 7");
   EXPECT_EQ(result.oid, ".1.3.6.1.2.1.");
   EXPECT_EQ(result.index, "");
   EXPECT_EQ(result.type, "INTEGER");
   EXPECT_EQ(result.value, "7");
}

TEST_F(HelpersBranchesShimTest, RemoveV3UserFromCacheCoversBothRemovalBranches) {
   static char sec_name[] = "alice";
   static unsigned char engine_id[] = "engine1";

   g_user1.secName = sec_name;
   g_user1.engineID = engine_id;
   g_user1.next = nullptr;
   g_user1.prev = nullptr;

   g_user_list = &g_user1;
   remove_v3_user_from_cache("alice", "engine1");
   EXPECT_EQ(g_usm_remove_calls, 1);
   EXPECT_EQ(g_usm_free_calls, 1);

   g_usm_remove_calls = 0;
   g_usm_free_calls = 0;

   g_user1.engineID = nullptr;
   g_user_list = &g_user1;
   remove_v3_user_from_cache("alice", "different_engine");
   EXPECT_EQ(g_usm_remove_calls, 1);
   EXPECT_EQ(g_usm_free_calls, 1);
}

TEST_F(HelpersBranchesShimTest, PrintObjidToStringCoversAllocFailAndOverflow) {
   oid name[] = {1, 3, 6, 1};

   g_fail_calloc = true;
   EXPECT_EQ(print_objid_to_string(name, OID_LENGTH(name)), "[TRUNCATED]\n");

   g_fail_calloc = false;
   g_force_objid_overflow = true;
   EXPECT_EQ(print_objid_to_string(name, OID_LENGTH(name)), "obj [TRUNCATED]\n");
}
