#include <gtest/gtest.h>

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