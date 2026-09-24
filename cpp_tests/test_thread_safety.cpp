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

TEST_F(ThreadSafetyTest, TestFormattingOptionsThreadIsolation) {
   SessionFormattingOptions opts_a;
   opts_a.print_oids_numerically = true;
   opts_a.print_enums_numerically = false;

   set_thread_formatting_options(opts_a);
   EXPECT_TRUE(get_thread_formatting_options().is_set);
   EXPECT_TRUE(get_thread_formatting_options().print_oids_numerically);
   EXPECT_FALSE(get_thread_formatting_options().print_enums_numerically);

   std::thread t([&]() {
      // In a new thread, formatting options must not be set initially
      auto opts_b = get_thread_formatting_options();
      EXPECT_FALSE(opts_b.is_set);
      EXPECT_FALSE(opts_b.print_oids_numerically);

      // Set thread B options
      SessionFormattingOptions new_b;
      new_b.print_enums_numerically = true;
      set_thread_formatting_options(new_b);

      EXPECT_TRUE(get_thread_formatting_options().is_set);
      EXPECT_TRUE(get_thread_formatting_options().print_enums_numerically);
      EXPECT_FALSE(get_thread_formatting_options().print_oids_numerically);
   });
   t.join();

   // Thread A's options must remain unaffected by Thread B
   EXPECT_TRUE(get_thread_formatting_options().is_set);
   EXPECT_TRUE(get_thread_formatting_options().print_oids_numerically);
   EXPECT_FALSE(get_thread_formatting_options().print_enums_numerically);

   clear_thread_formatting_options();
   EXPECT_FALSE(get_thread_formatting_options().is_set);
}

TEST_F(ThreadSafetyTest, TestFormattingScopeRAII) {
   EXPECT_FALSE(get_thread_formatting_options().is_set);
   {
      SessionFormattingOptions opts;
      opts.print_full_oids = true;
      FormattingScope scope(opts);

      EXPECT_TRUE(get_thread_formatting_options().is_set);
      EXPECT_TRUE(get_thread_formatting_options().print_full_oids);
   }
   EXPECT_FALSE(get_thread_formatting_options().is_set);
}