#include <gtest/gtest.h>

#include "datatypesbase.h"

TEST(ResultTest, BasicResultTest) {
   ResultBase r1;
   r1.oid = "SNMPv2-MIB::sysDescr";
   r1.index = "0";
   r1.type = "STRING";
   r1.value = "Test Description";

   EXPECT_EQ(r1._to_string(),
             "oid: SNMPv2-MIB::sysDescr, index: 0, type: STRING, value: Test Description");
}

TEST(ResultTest, EmptyFieldsTest) {
   ResultBase r2;
   r2.oid = "";
   r2.index = "";
   r2.type = "";
   r2.value = "";

   EXPECT_EQ(r2._to_string(), "oid: , index: , type: , value: ");
}

TEST(ResultTest, SpecialCharactersTest) {
   ResultBase r3;
   r3.oid = "test::oid";
   r3.index = "123";
   r3.type = "INTEGER";
   r3.value = "456";

   EXPECT_EQ(r3._to_string(), "oid: test::oid, index: 123, type: INTEGER, value: 456");
}

TEST(ResultTest, NegativeIntegerTest) {
   ResultBase r4;
   r4.oid = "test::oid";
   r4.index = "123";
   r4.type = "INTEGER";
   r4.value = "-456";

   EXPECT_EQ(r4._to_string(), "oid: test::oid, index: 123, type: INTEGER, value: -456");
}

TEST(ResultTest, EmptyValueTest) {
   ResultBase r5;
   r5.oid = "test::oid";
   r5.index = "123";
   r5.type = "INTEGER";
   r5.value = "";

   EXPECT_EQ(r5._to_string(), "oid: test::oid, index: 123, type: INTEGER, value: ");
}

TEST(ResultTest, AssignmentOperatorTest) {
   ResultBase r1;
   r1.oid = "test::oid";
   r1.index = "123";
   r1.type = "INTEGER";
   r1.value = "456";

   ResultBase r2;
   r2 = r1;
   EXPECT_EQ(r1._to_string(), r2._to_string());

   // Modify r2 after assignment
   r2.oid = "new::oid";
   r2.value = "789";

   // r1 should remain unchanged
   EXPECT_EQ(r1.oid, "test::oid");
   EXPECT_EQ(r1.index, "123");
   EXPECT_EQ(r1.type, "INTEGER");
   EXPECT_EQ(r1.value, "456");
   EXPECT_EQ(r1._to_string(), "oid: test::oid, index: 123, type: INTEGER, value: 456");

   // r2 should have the modified values
   EXPECT_EQ(r2.oid, "new::oid");
   EXPECT_EQ(r2.index, "123");
   EXPECT_EQ(r2.type, "INTEGER");
   EXPECT_EQ(r2.value, "789");
   EXPECT_EQ(r2._to_string(), "oid: new::oid, index: 123, type: INTEGER, value: 789");
}

TEST(ResultTest, MoveOperatorTest) {
   ResultBase r1;
   r1.oid = "test::oid";
   r1.index = "123";
   r1.type = "INTEGER";
   r1.value = "456";

   ResultBase r2;
   r2 = std::move(r1);

   EXPECT_EQ(r2.oid, "test::oid");
   EXPECT_EQ(r2.index, "123");
   EXPECT_EQ(r2.type, "INTEGER");
   EXPECT_EQ(r2.value, "456");

   EXPECT_TRUE(r1.oid.empty());
}
TEST(ResultTest, VectorOfResultsTest) {
   std::vector<ResultBase> results;

   ResultBase r1;
   r1.oid = "oid1";
   r1.index = "1";
   r1.type = "STRING";
   r1.value = "value1";

   ResultBase r2;
   r2.oid = "oid2";
   r2.index = "2";
   r2.type = "INTEGER";
   r2.value = "123";

   results.push_back(r1);
   results.push_back(r2);

   EXPECT_EQ(results.size(), 2);
   EXPECT_EQ(results[0]._to_string(), "oid: oid1, index: 1, type: STRING, value: value1");
   EXPECT_EQ(results[1]._to_string(), "oid: oid2, index: 2, type: INTEGER, value: 123");

   // Test modifying vector elements
   results[0].value = "new_value";
   EXPECT_EQ(results[0]._to_string(), "oid: oid1, index: 1, type: STRING, value: new_value");
}
TEST(ConvertedValueTest, IntegerType) {
   auto cv = _make_converted_value("INTEGER", "42");
   ASSERT_TRUE(std::holds_alternative<int>(cv));
   EXPECT_EQ(std::get<int>(cv), 42);

   cv = _make_converted_value("INTEGER32", "-123");
   ASSERT_TRUE(std::holds_alternative<int>(cv));
   EXPECT_EQ(std::get<int>(cv), -123);
}

TEST(ConvertedValueTest, UnsignedIntegerType) {
   auto cv = _make_converted_value("UINTEGER", "123");
   ASSERT_TRUE(std::holds_alternative<uint32_t>(cv));
   EXPECT_EQ(std::get<uint32_t>(cv), 123u);

   cv = _make_converted_value("UNSIGNED32", "456");
   ASSERT_TRUE(std::holds_alternative<uint32_t>(cv));
   EXPECT_EQ(std::get<uint32_t>(cv), 456u);

   cv = _make_converted_value("GAUGE", "789");
   ASSERT_TRUE(std::holds_alternative<uint32_t>(cv));
   EXPECT_EQ(std::get<uint32_t>(cv), 789u);

   cv = _make_converted_value("COUNTER", "321");
   ASSERT_TRUE(std::holds_alternative<uint32_t>(cv));
   EXPECT_EQ(std::get<uint32_t>(cv), 321u);
}

TEST(ConvertedValueTest, Counter64Type) {
   auto cv = _make_converted_value("COUNTER64", "1234567890123");
   ASSERT_TRUE(std::holds_alternative<uint64_t>(cv));
   EXPECT_EQ(std::get<uint64_t>(cv), 1234567890123ull);
}

TEST(ConvertedValueTest, TimeTicksType) {
   auto cv = _make_converted_value("TIMETICKS", "(107129) 0:17:51.29");
   ASSERT_TRUE(std::holds_alternative<uint32_t>(cv));
   EXPECT_EQ(std::get<uint32_t>(cv), 107129u);
}

TEST(ConvertedValueTest, StringLikeTypes) {
   std::vector<std::string> types = {
       "OCTETSTR",   "STRING",    "OBJID",       "OBJIDENTITY", "NETADDR",   "IPADDR",
       "OPAQUE",     "BITSTRING", "NSAPADDRESS", "TRAPTYPE",    "NOTIFTYPE", "OBJGROUP",
       "NOTIFGROUP", "MODID",     "AGENTCAP",    "MODCOMP",     "NULL",      "OTHER"};
   for (auto const& type : types) {
      auto cv = _make_converted_value(type, "test_value");
      ASSERT_TRUE(std::holds_alternative<std::string>(cv));
      EXPECT_EQ(std::get<std::string>(cv), "test_value");
   }
}

TEST(ConvertedValueTest, UnknownTypeFallback) {
   auto cv = _make_converted_value("UNKNOWN_TYPE", "fallback_value");
   ASSERT_TRUE(std::holds_alternative<std::string>(cv));
   EXPECT_EQ(std::get<std::string>(cv), "fallback_value");
}

TEST(ConvertedValueTest, InvalidIntegerThrows) {
   EXPECT_THROW(_make_converted_value("INTEGER", "notanint"), std::invalid_argument);
}

TEST(ConvertedValueTest, InvalidUnsignedThrows) {
   EXPECT_THROW(_make_converted_value("UNSIGNED32", "notanuint"), std::invalid_argument);
}

TEST(ConvertedValueTest, InvalidCounter64Throws) {
   EXPECT_THROW(_make_converted_value("COUNTER64", "notauint64"), std::invalid_argument);
}

TEST(ConvertedValueTest, InvalidTimeTicksThrows) {
   EXPECT_THROW(_make_converted_value("TIMETICKS", "notadouble"), std::invalid_argument);
}
