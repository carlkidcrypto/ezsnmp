#include <gtest/gtest.h>

#include <algorithm>
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
usmUser g_user3{};
usmUser g_user4{};
usmUser *g_user_list = nullptr;
int g_usm_remove_calls = 0;
int g_usm_free_calls = 0;
std::vector<usmUser *> g_removed_users;
std::vector<usmUser *> g_freed_users;
std::vector<unsigned char *> g_freed_engine_id_pointers;
std::vector<std::vector<unsigned char>> g_freed_engine_ids;
std::vector<size_t> g_freed_engine_id_lengths;
std::vector<std::string> g_cache_events;

void reset_shim_state() {
   g_fail_calloc = false;
   g_fail_strdup = false;
   g_force_sprint_variable_fail = false;
   g_force_objid_overflow = false;

   g_user1 = usmUser{};
   g_user2 = usmUser{};
   g_user3 = usmUser{};
   g_user4 = usmUser{};
   g_user_list = nullptr;
   g_usm_remove_calls = 0;
   g_usm_free_calls = 0;
   g_removed_users.clear();
   g_freed_users.clear();
   g_freed_engine_id_pointers.clear();
   g_freed_engine_ids.clear();
   g_freed_engine_id_lengths.clear();
   g_cache_events.clear();
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
   g_removed_users.push_back(user);
   g_cache_events.push_back("remove");
   return user;
}

extern "C" usmUser *usm_free_user(usmUser *user) {
   ++g_usm_free_calls;
   g_freed_users.push_back(user);
   g_cache_events.push_back("free_user");
   return user;
}

extern "C" void free_enginetime(unsigned char *engine_id, size_t engine_id_length) {
   g_freed_engine_id_pointers.push_back(engine_id);
   g_freed_engine_ids.emplace_back(engine_id, engine_id + engine_id_length);
   g_freed_engine_id_lengths.push_back(engine_id_length);
   g_cache_events.push_back("free_enginetime");
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

TEST_F(HelpersBranchesShimTest, DeleterFreesOuterArrayAndStrings) {
   // Verify that the Deleter frees both the strdup'd strings AND the outer char** array.
   // The outer array was previously leaked (only strdup'd strings were freed).
   // Running under AddressSanitizer or Valgrind will detect any remaining leak.
   int argc = 0;
   {
      auto argv = create_argv({"-v", "2c", "-c", "public"}, argc);
      EXPECT_EQ(argc, 5);
      EXPECT_STREQ(argv[0], "netsnmp");
      EXPECT_STREQ(argv[1], "-v");
      EXPECT_STREQ(argv[4], "public");
      EXPECT_EQ(argv[5], nullptr);
      // unique_ptr goes out of scope here; Deleter must free both the
      // strdup'd elements AND the outer char** allocation (delete[] ptr).
   }
   SUCCEED();
}

TEST_F(HelpersBranchesShimTest, DeleterCalledDirectlyFreesArrayAndStrings) {
   // Directly invoke the Deleter on a manually constructed argv array to confirm
   // it frees the outer allocation as well as individual strdup'd strings.
   constexpr int kArgc = 3;
   char **arr = new char *[kArgc + 1]();
   arr[0] = const_cast<char *>("netsnmp"); // argv[0] is never freed by Deleter
   arr[1] = strdup("arg1");
   ASSERT_NE(arr[1], nullptr);
   arr[2] = strdup("arg2");
   ASSERT_NE(arr[2], nullptr);
   arr[3] = nullptr;

   Deleter d;
   d(arr); // frees arr[1], arr[2], then delete[] arr — no leaks or double-frees
   SUCCEED();
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

TEST_F(HelpersBranchesShimTest, ParseResultWithoutTypeDelimiterPreservesLegacyBehavior) {
   auto result = parse_result("SNMPv2-MIB::sysDescr.0 = value_without_colon");
   EXPECT_EQ(result.oid, "SNMPv2-MIB::sysDescr");
   EXPECT_EQ(result.index, "0");
   EXPECT_EQ(result.type, "value_without_colon");
   EXPECT_EQ(result.value, "value_without_colon");
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

TEST_F(HelpersBranchesShimTest, RemoveV3UserFromCacheNoMatchWalksListWithoutRemoval) {
   static char sec_name_1[] = "alice";
   static unsigned char engine_id_1[] = "engine1";
   static char sec_name_2[] = "bob";
   static unsigned char engine_id_2[] = "engine2";

   g_user1.secName = sec_name_1;
   g_user1.engineID = engine_id_1;
   g_user1.next = &g_user2;
   g_user1.prev = nullptr;

   g_user2.secName = sec_name_2;
   g_user2.engineID = engine_id_2;
   g_user2.next = nullptr;
   g_user2.prev = &g_user1;

   g_user_list = &g_user1;
   remove_v3_user_from_cache("charlie", "engine3");
   EXPECT_EQ(g_usm_remove_calls, 0);
   EXPECT_EQ(g_usm_free_calls, 0);
}

TEST_F(HelpersBranchesShimTest, RemoveV3UserFromCacheClearsAllMatchingUsersAndEngineTimes) {
   static char alice[] = "alice";
   static char bob[] = "bob";
   static unsigned char binary_engine_id[] = {0x80, 0x00, 0x1f, 0x88, 0xff};
   static unsigned char second_engine_id[] = {0x01, 0x00, 0x02};

   g_user1.secName = alice;
   g_user1.engineID = binary_engine_id;
   g_user1.engineIDLen = sizeof(binary_engine_id);
   g_user1.next = &g_user2;

   g_user2.secName = bob;
   g_user2.engineID = binary_engine_id;
   g_user2.engineIDLen = sizeof(binary_engine_id);
   g_user2.prev = &g_user1;
   g_user2.next = &g_user3;

   g_user3.secName = alice;
   g_user3.engineID = nullptr;
   g_user3.engineIDLen = 0;
   g_user3.prev = &g_user2;
   g_user3.next = &g_user4;

   g_user4.secName = alice;
   g_user4.engineID = second_engine_id;
   g_user4.engineIDLen = sizeof(second_engine_id);
   g_user4.prev = &g_user3;

   g_user_list = &g_user1;
   remove_v3_user_from_cache("alice", "ignored-context-engine-id");

   EXPECT_EQ(g_removed_users, (std::vector<usmUser *>{&g_user1, &g_user3, &g_user4}));
   EXPECT_EQ(g_freed_users, g_removed_users);
   ASSERT_EQ(g_freed_engine_id_pointers.size(), 2u);
   EXPECT_EQ(g_freed_engine_id_pointers[0], binary_engine_id);
   EXPECT_EQ(g_freed_engine_id_pointers[1], second_engine_id);
   EXPECT_EQ(g_freed_engine_id_lengths,
             (std::vector<size_t>{sizeof(binary_engine_id), sizeof(second_engine_id)}));
   EXPECT_EQ(
       g_freed_engine_ids[0],
       (std::vector<unsigned char>(binary_engine_id, binary_engine_id + sizeof(binary_engine_id))));
   EXPECT_EQ(
       g_freed_engine_ids[1],
       (std::vector<unsigned char>(second_engine_id, second_engine_id + sizeof(second_engine_id))));
   EXPECT_EQ(g_cache_events,
             (std::vector<std::string>{"free_enginetime", "remove", "free_user", "remove",
                                       "free_user", "free_enginetime", "remove", "free_user"}));

   EXPECT_EQ(std::find(g_removed_users.begin(), g_removed_users.end(), &g_user2),
             g_removed_users.end());
   EXPECT_EQ(std::find(g_freed_users.begin(), g_freed_users.end(), &g_user2), g_freed_users.end());
   EXPECT_EQ(g_user2.secName, bob);
}

TEST_F(HelpersBranchesShimTest, PrintObjidToStringCoversAllocFailAndOverflow) {
   oid name[] = {1, 3, 6, 1};

   g_fail_calloc = true;
   EXPECT_EQ(print_objid_to_string(name, OID_LENGTH(name)), "[TRUNCATED]\n");

   g_fail_calloc = false;
   g_force_objid_overflow = true;
   EXPECT_EQ(print_objid_to_string(name, OID_LENGTH(name)), "obj [TRUNCATED]\n");
}
