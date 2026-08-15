#include <gtest/gtest.h>

#include <atomic>
#include <thread>
#include <vector>

#include "thread_safety.h"

class ThreadSafetyTest : public ::testing::Test {
  protected:
   void SetUp() override {
      // Reset globals for test
      g_netsnmp_init_count.store(0);
      g_netsnmp_initialized.store(false);
   }
};

TEST_F(ThreadSafetyTest, TestInitAndCleanup) {
   // First init should initialize
   netsnmp_thread_init("test_app");
   EXPECT_EQ(g_netsnmp_init_count.load(), 1);
   EXPECT_TRUE(g_netsnmp_initialized.load());

   // Second init should not initialize again
   netsnmp_thread_init("test_app");
   EXPECT_EQ(g_netsnmp_init_count.load(), 2);
   EXPECT_TRUE(g_netsnmp_initialized.load());

   // First cleanup should not cleanup
   netsnmp_thread_cleanup("test_app");
   EXPECT_EQ(g_netsnmp_init_count.load(), 1);
   EXPECT_TRUE(g_netsnmp_initialized.load());

   // Second cleanup should cleanup
   netsnmp_thread_cleanup("test_app");
   EXPECT_EQ(g_netsnmp_init_count.load(), 0);
   EXPECT_FALSE(g_netsnmp_initialized.load());
}

// Calling cleanup more times than init should not crash (count goes negative
// but snmp_shutdown is only triggered when count transitions 1 → 0).
TEST_F(ThreadSafetyTest, TestOverCleanupDoesNotCrash) {
   // Start from zero count: cleanup should safely decrement below zero
   netsnmp_thread_cleanup("test_app");
   EXPECT_EQ(g_netsnmp_init_count.load(), -1);
   EXPECT_FALSE(g_netsnmp_initialized.load());

   // Restore to zero so subsequent tests start from a consistent state
   g_netsnmp_init_count.store(0);
}

// Multiple threads concurrently calling init followed by cleanup should leave
// the reference count and initialized flag in a consistent final state.
TEST_F(ThreadSafetyTest, TestConcurrentInitCleanup) {
   constexpr int kThreads = 8;

   std::vector<std::thread> threads;
   threads.reserve(kThreads);
   for (int i = 0; i < kThreads; ++i) {
      threads.emplace_back([i]() {
         netsnmp_thread_init("test_app_" + std::to_string(i));
         netsnmp_thread_cleanup("test_app_" + std::to_string(i));
      });
   }
   for (auto& t : threads) {
      t.join();
   }

   // After every init is matched by a cleanup the count must be back to zero
   EXPECT_EQ(g_netsnmp_init_count.load(), 0);
   EXPECT_FALSE(g_netsnmp_initialized.load());
}