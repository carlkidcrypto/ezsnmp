#include <gtest/gtest.h>

#include "thread_safety.h"

TEST(ThreadSafetyTest, TestInitAndCleanup) {
    // Reset globals for test
    g_netsnmp_init_count.store(0);
    g_netsnmp_initialized.store(false);

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