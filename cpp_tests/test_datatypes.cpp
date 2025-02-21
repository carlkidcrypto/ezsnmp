#include <gtest/gtest.h>
#include "datatypes.h"

TEST(ResultTest, ToStringTest) {
   // Test case 1: Basic result object
   Result r1;
   r1.oid = "SNMPv2-MIB::sysDescr";
   r1.index = "0"; 
   r1.type = "STRING";
   r1.value = "Test Description";
   
   EXPECT_EQ(r1.to_string(), 
      "oid: SNMPv2-MIB::sysDescr, index: 0, type: STRING, value: Test Description");

   // Test case 2: Empty fields
   Result r2;
   r2.oid = "";
   r2.index = "";
   r2.type = "";
   r2.value = "";
   
   EXPECT_EQ(r2.to_string(),
      "oid: , index: , type: , value: ");

   // Test case 3: Special characters
   Result r3;
   r3.oid = "test::oid";
   r3.index = "123";
   r3.type = "INTEGER";
   r3.value = "456";

   EXPECT_EQ(r3.to_string(),
      "oid: test::oid, index: 123, type: INTEGER, value: 456");
}