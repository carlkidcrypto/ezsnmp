#include <gtest/gtest.h>

#include <algorithm>
#include <chrono>
#include <condition_variable>
#include <future>
#include <mutex>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include "sessionbase.h"

namespace {

enum class GetBehavior { Return, Throw, Block };

std::mutex g_state_mutex;
std::condition_variable g_state_changed;
GetBehavior g_get_behavior = GetBehavior::Return;
bool g_release_get = false;
int g_entered_gets = 0;
int g_active_gets = 0;
int g_max_active_gets = 0;
std::vector<std::pair<std::string, std::string>> g_cache_removals;

void reset_shim_state() {
   std::lock_guard<std::mutex> lock(g_state_mutex);
   g_get_behavior = GetBehavior::Return;
   g_release_get = false;
   g_entered_gets = 0;
   g_active_gets = 0;
   g_max_active_gets = 0;
   g_cache_removals.clear();
}

SessionBase make_v3_session(std::string const &username, std::string const &context_engine_id) {
   return SessionBase("localhost", "161", "3", "", "", "", "", context_engine_id, "noAuthNoPriv",
                      "", username);
}

std::vector<Result> empty_result(std::vector<std::string> const &, std::string const &) {
   return {};
}

} // namespace

void remove_v3_user_from_cache(std::string const &security_name,
                               std::string const &context_engine_id) {
   std::lock_guard<std::mutex> lock(g_state_mutex);
   g_cache_removals.emplace_back(security_name, context_engine_id);
}

std::vector<Result> snmpwalk(std::vector<std::string> const &args,
                             std::string const &init_app_name) {
   return empty_result(args, init_app_name);
}

std::vector<Result> snmpbulkwalk(std::vector<std::string> const &args,
                                 std::string const &init_app_name) {
   return empty_result(args, init_app_name);
}

std::vector<Result> snmpget(std::vector<std::string> const &, std::string const &) {
   std::unique_lock<std::mutex> lock(g_state_mutex);
   ++g_entered_gets;
   ++g_active_gets;
   g_max_active_gets = std::max(g_max_active_gets, g_active_gets);
   g_state_changed.notify_all();

   if (g_get_behavior == GetBehavior::Throw) {
      --g_active_gets;
      throw std::runtime_error("shim failure");
   }
   if (g_get_behavior == GetBehavior::Block) {
      g_state_changed.wait(lock, [] { return g_release_get; });
   }

   --g_active_gets;
   return {};
}

std::vector<Result> snmpgetnext(std::vector<std::string> const &args,
                                std::string const &init_app_name) {
   return empty_result(args, init_app_name);
}

std::vector<Result> snmpbulkget(std::vector<std::string> const &args,
                                std::string const &init_app_name) {
   return empty_result(args, init_app_name);
}

std::vector<Result> snmpset(std::vector<std::string> const &args,
                            std::string const &init_app_name) {
   return empty_result(args, init_app_name);
}

class SessionBaseV3GuardShimTest : public ::testing::Test {
  protected:
   void SetUp() override { reset_shim_state(); }
};

TEST_F(SessionBaseV3GuardShimTest, CleansCacheBeforeAndAfterException) {
   // Real SNMPv3 engine IDs are opaque binary data, so include NUL and non-ASCII bytes.
   std::string const binary_context_engine_id("\x80\x00\xff", 3);
   SessionBase session = make_v3_session("alice", binary_context_engine_id);
   g_get_behavior = GetBehavior::Throw;

   EXPECT_THROW((void)session.get(".1.3.6.1.2.1.1.1.0"), std::runtime_error);

   std::vector<std::pair<std::string, std::string>> const expected = {
       {"alice", binary_context_engine_id}, {"alice", binary_context_engine_id}};
   EXPECT_EQ(g_cache_removals, expected);
}

TEST_F(SessionBaseV3GuardShimTest, SerializesConcurrentV3OperationsAndTheirCleanup) {
   SessionBase first = make_v3_session("alice", "engine-a");
   SessionBase second = make_v3_session("bob", "engine-b");
   g_get_behavior = GetBehavior::Block;

   auto first_get = std::async(std::launch::async, [&first] { return first.get(".1"); });
   {
      std::unique_lock<std::mutex> lock(g_state_mutex);
      ASSERT_TRUE(g_state_changed.wait_for(lock, std::chrono::seconds(2),
                                           [] { return g_entered_gets == 1; }));
   }

   auto second_get = std::async(std::launch::async, [&second] { return second.get(".1"); });
   {
      std::unique_lock<std::mutex> lock(g_state_mutex);
      EXPECT_FALSE(g_state_changed.wait_for(lock, std::chrono::milliseconds(100),
                                            [] { return g_entered_gets > 1; }));
      EXPECT_EQ(g_max_active_gets, 1);
      g_release_get = true;
   }
   g_state_changed.notify_all();

   EXPECT_TRUE(first_get.get().empty());
   EXPECT_TRUE(second_get.get().empty());
   EXPECT_EQ(g_entered_gets, 2);
   EXPECT_EQ(g_max_active_gets, 1);

   std::vector<std::pair<std::string, std::string>> const expected = {
       {"alice", "engine-a"}, {"alice", "engine-a"}, {"bob", "engine-b"}, {"bob", "engine-b"}};
   EXPECT_EQ(g_cache_removals, expected);
}
