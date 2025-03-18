#include <gtest/gtest.h>

#include "datatypes.h"

TEST(ResultTest, BasicResultTest) {
   Result r1;
   r1.oid = "SNMPv2-MIB::sysDescr";
   r1.index = "0";
   r1.type = "STRING";
   r1.value = "Test Description";

   EXPECT_EQ(r1.to_string(),
             "oid: SNMPv2-MIB::sysDescr, index: 0, type: STRING, value: Test Description");
}

TEST(ResultTest, EmptyFieldsTest) {
   Result r2;
   r2.oid = "";
   r2.index = "";
   r2.type = "";
   r2.value = "";

   EXPECT_EQ(r2.to_string(), "oid: , index: , type: , value: ");
}

TEST(ResultTest, SpecialCharactersTest) {
   Result r3;
   r3.oid = "test::oid";
   r3.index = "123";
   r3.type = "INTEGER";
   r3.value = "456";

   EXPECT_EQ(r3.to_string(), "oid: test::oid, index: 123, type: INTEGER, value: 456");
}

TEST(ResultTest, NegativeIntegerTest) {
   Result r4;
   r4.oid = "test::oid";
   r4.index = "123";
   r4.type = "INTEGER";
   r4.value = "-456";

   EXPECT_EQ(r4.to_string(), "oid: test::oid, index: 123, type: INTEGER, value: -456");
}

TEST(ResultTest, EmptyValueTest) {
   Result r5;
   r5.oid = "test::oid";
   r5.index = "123";
   r5.type = "INTEGER";
   r5.value = "";

   EXPECT_EQ(r5.to_string(), "oid: test::oid, index: 123, type: INTEGER, value: ");
}

TEST(ResultTest, AssignmentOperatorTest) {
   Result r1;
   r1.oid = "test::oid";
   r1.index = "123";
   r1.type = "INTEGER";
   r1.value = "456";

   Result r2;
   r2 = r1;
   EXPECT_EQ(r1.to_string(), r2.to_string());
   
   // Modify r2 after assignment
   r2.oid = "new::oid";
   r2.value = "789";

   // r1 should remain unchanged
   EXPECT_EQ(r1.oid, "test::oid");
   EXPECT_EQ(r1.index, "123");
   EXPECT_EQ(r1.type, "INTEGER");
   EXPECT_EQ(r1.value, "456");
   EXPECT_EQ(r1.to_string(), "oid: test::oid, index: 123, type: INTEGER, value: 456");

   // r2 should have the modified values
   EXPECT_EQ(r2.oid, "new::oid");
   EXPECT_EQ(r2.index, "123");
   EXPECT_EQ(r2.type, "INTEGER");
   EXPECT_EQ(r2.value, "789");
   EXPECT_EQ(r2.to_string(), "oid: new::oid, index: 123, type: INTEGER, value: 789");
}

TEST(ResultTest, MoveOperatorTest) {
   Result r1;
   r1.oid = "test::oid";
   r1.index = "123";
   r1.type = "INTEGER";
   r1.value = "456";

   Result r2;
   r2 = std::move(r1);

   EXPECT_EQ(r2.oid, "test::oid");
   EXPECT_EQ(r2.index, "123");
   EXPECT_EQ(r2.type, "INTEGER");
   EXPECT_EQ(r2.value, "456");

   EXPECT_TRUE(r1.oid.empty());
}
TEST(ResultTest, VectorOfResultsTest) {
   std::vector<Result> results;
   
   Result r1;
   r1.oid = "oid1";
   r1.index = "1";
   r1.type = "STRING"; 
   r1.value = "value1";
   
   Result r2;
   r2.oid = "oid2";
   r2.index = "2";
   r2.type = "INTEGER";
   r2.value = "123";
   
   results.push_back(r1);
   results.push_back(r2);

   EXPECT_EQ(results.size(), 2);
   EXPECT_EQ(results[0].to_string(), "oid: oid1, index: 1, type: STRING, value: value1");
   EXPECT_EQ(results[1].to_string(), "oid: oid2, index: 2, type: INTEGER, value: 123");

   // Test modifying vector elements
   results[0].value = "new_value";
   EXPECT_EQ(results[0].to_string(), "oid: oid1, index: 1, type: STRING, value: new_value");
}

