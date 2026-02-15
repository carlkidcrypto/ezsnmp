#include <gtest/gtest.h>

#include <thread>
#include <vector>

#include "snmpset.h"
#include "snmpwalk.h"
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

// Test concurrent snmpwalk calls to verify thread-local variables work correctly
TEST_F(ThreadSafetyTest, TestConcurrentSnmpwalkCalls) {
   // Test that concurrent snmpwalk calls with different options don't interfere
   auto walk_with_timeout = [](int thread_id) {
      std::vector<std::string> args = {"-v",
                                       "2c",
                                       "-c",
                                       "public",
                                       "-t",
                                       "1",
                                       "127.0.0.1:11162",
                                       "SNMPv2-MIB::sysORDescr"};
      try {
         auto results = snmpwalk(args, "test_walk_" + std::to_string(thread_id));
         // Should timeout
         FAIL() << "Expected TimeoutErrorBase but got success";
      } catch (TimeoutErrorBase const& e) {
         // Expected - verify error message contains timeout info
         std::string error_msg(e.what());
         EXPECT_TRUE(error_msg.find("Timeout") != std::string::npos ||
                     error_msg.find("127.0.0.1") != std::string::npos);
      } catch (...) {
         // Unexpected exception type
         FAIL() << "Expected TimeoutErrorBase but got different exception";
      }
   };

   // Run multiple concurrent walks
   std::vector<std::thread> threads;
   for (int i = 0; i < 3; ++i) {
      threads.emplace_back(walk_with_timeout, i);
   }

   for (auto& t : threads) {
      t.join();
   }
}

// Test concurrent snmpset calls with quiet flag to verify thread-local storage
TEST_F(ThreadSafetyTest, TestConcurrentSnmpsetQuietFlag) {
   // Thread 1: Uses quiet flag
   auto set_with_quiet = []() {
      std::vector<std::string> args = {
          "-v", "2c", "-c", "public", "-Cq", "localhost:11161", "SNMPv2-MIB::sysLocation.0", "s",
          "test quiet"};
      auto results = snmpset(args, "test_set_quiet");
      // With -Cq flag, should return empty results
      EXPECT_TRUE(results.empty());
   };

   // Thread 2: Uses no quiet flag
   auto set_without_quiet = []() {
      std::vector<std::string> args = {
          "-v", "2c", "-c", "public", "localhost:11161", "SNMPv2-MIB::sysLocation.0", "s",
          "test normal"};
      auto results = snmpset(args, "test_set_normal");
      // Without -Cq flag, should return results
      EXPECT_FALSE(results.empty());
   };

   // Run both concurrently
   std::thread t1(set_with_quiet);
   std::thread t2(set_without_quiet);

   t1.join();
   t2.join();
}

// Test concurrent snmpwalk with -CE (end OID) option to verify thread-local end_name
TEST_F(ThreadSafetyTest, TestConcurrentSnmpwalkEndOid) {
   // Thread 1: Uses -CE option with one end OID
   auto walk_with_end_oid_1 = []() {
      std::vector<std::string> args = {"-v",
                                       "2c",
                                       "-c",
                                       "public",
                                       "-CE",
                                       "SNMPv2-MIB::sysORDescr.2",
                                       "localhost:11161",
                                       "SNMPv2-MIB::sysORDescr"};
      auto results = snmpwalk(args, "test_walk_end1");
      EXPECT_FALSE(results.empty());
   };

   // Thread 2: Uses -CE option with different end OID
   auto walk_with_end_oid_2 = []() {
      std::vector<std::string> args = {"-v",
                                       "2c",
                                       "-c",
                                       "public",
                                       "-CE",
                                       "SNMPv2-MIB::sysORDescr.5",
                                       "localhost:11161",
                                       "SNMPv2-MIB::sysORDescr"};
      auto results = snmpwalk(args, "test_walk_end2");
      EXPECT_FALSE(results.empty());
   };

   // Run both concurrently
   std::thread t1(walk_with_end_oid_1);
   std::thread t2(walk_with_end_oid_2);

   t1.join();
   t2.join();
}