#include <gtest/gtest.h>

#include "datatypes.h"

TEST(ResultTest, BasicResultTest) {
   Result r1;
   r1.oid = "SNMPv2-MIB::sysDescr";
   r1.index = "0";
   r1.type = "STRING";
   r1.value = "Test Description";

   EXPECT_EQ(r1._to_string(),
             "oid: SNMPv2-MIB::sysDescr, index: 0, type: STRING, value: Test Description");
}

TEST(ResultTest, EmptyFieldsTest) {
   Result r2;
   r2.oid = "";
   r2.index = "";
   r2.type = "";
   r2.value = "";

   EXPECT_EQ(r2._to_string(), "oid: , index: , type: , value: ");
}

TEST(ResultTest, SpecialCharactersTest) {
   Result r3;
   r3.oid = "test::oid";
   r3.index = "123";
   r3.type = "INTEGER";
   r3.value = "456";

   EXPECT_EQ(r3._to_string(), "oid: test::oid, index: 123, type: INTEGER, value: 456");
}

TEST(ResultTest, NegativeIntegerTest) {
   Result r4;
   r4.oid = "test::oid";
   r4.index = "123";
   r4.type = "INTEGER";
   r4.value = "-456";

   EXPECT_EQ(r4._to_string(), "oid: test::oid, index: 123, type: INTEGER, value: -456");
}

TEST(ResultTest, EmptyValueTest) {
   Result r5;
   r5.oid = "test::oid";
   r5.index = "123";
   r5.type = "INTEGER";
   r5.value = "";

   EXPECT_EQ(r5._to_string(), "oid: test::oid, index: 123, type: INTEGER, value: ");
}

TEST(ResultTest, AssignmentOperatorTest) {
   Result r1;
   r1.oid = "test::oid";
   r1.index = "123";
   r1.type = "INTEGER";
   r1.value = "456";

   Result r2;
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
   EXPECT_EQ(results[0]._to_string(), "oid: oid1, index: 1, type: STRING, value: value1");
   EXPECT_EQ(results[1]._to_string(), "oid: oid2, index: 2, type: INTEGER, value: 123");

   // Test modifying vector elements
   results[0].value = "new_value";
   EXPECT_EQ(results[0]._to_string(), "oid: oid1, index: 1, type: STRING, value: new_value");
}

// Test fixture for accessing private members of Result
class ResultConvertedValueTest : public ::testing::Test {
protected:
    Result result_obj;
};

// Test for INTEGER type conversion
TEST_F(ResultConvertedValueTest, HandlesInteger) {
    auto converted = result_obj._make_converted_value("INTEGER", "4");
    EXPECT_EQ(std::get<int>(converted), 4);
}

// Test for Counter32 type conversion
TEST_F(ResultConvertedValueTest, HandlesCounter32) {
    auto converted = result_obj._make_converted_value("Counter32", "1738754");
    EXPECT_EQ(std::get<uint32_t>(converted), 1738754);
}

// Test for Counter64 type conversion
TEST_F(ResultConvertedValueTest, HandlesCounter64) {
    auto converted = result_obj._make_converted_value("Counter64", "22711");
    EXPECT_EQ(std::get<uint64_t>(converted), 22711);
}

// Test for Timeticks type conversion
TEST_F(ResultConvertedValueTest, HandlesTimeticks) {
    auto converted = result_obj._make_converted_value("Timeticks", "(3410517) 9:28:25.17");
    EXPECT_EQ(std::get<uint32_t>(converted), 3410517);
}

// Test for Timeticks type conversion with value as integer
TEST_F(ResultConvertedValueTest, HandlesTimeticksAsInteger) {
    auto converted = result_obj._make_converted_value("Timeticks", "3410517");
    EXPECT_EQ(std::get<uint32_t>(converted), 3410517);
}

// Test for Gauge32 type conversion
TEST_F(ResultConvertedValueTest, HandlesGauge32) {
    auto converted = result_obj._make_converted_value("Gauge32", "10000000");
    EXPECT_EQ(std::get<uint32_t>(converted), 10000000);
}

// Test for STRING type, which should not be converted
TEST_F(ResultConvertedValueTest, HandlesString) {
    auto converted = result_obj._make_converted_value("STRING", "Some long string value");
    EXPECT_EQ(std::get<std::string>(converted), "No Conversion Available");
}

// Test for OID type, which should not be converted
TEST_F(ResultConvertedValueTest, HandlesOid) {
    auto converted = result_obj._make_converted_value("OID", "SNMP-FRAMEWORK-MIB::snmpFrameworkMIBCompliance");
    EXPECT_EQ(std::get<std::string>(converted), "No Conversion Available");
}

// Test for IpAddress type, which should not be converted
TEST_F(ResultConvertedValueTest, HandlesIpAddress) {
    auto converted = result_obj._make_converted_value("IpAddress", "172.25.10.171");
    EXPECT_EQ(std::get<std::string>(converted), "No Conversion Available");
}

// Test for an unknown type
TEST_F(ResultConvertedValueTest, HandlesUnknownType) {
    auto converted = result_obj._make_converted_value("Hex-STRING", "00 15 5D 6E 34 05");
    EXPECT_EQ(std::get<std::string>(converted), "Unknown Conversion");
}

// Test for a value that is not a valid integer
TEST_F(ResultConvertedValueTest, HandlesInvalidInteger) {
    auto converted = result_obj._make_converted_value("INTEGER", "not-a-number");
    EXPECT_EQ(std::get<std::string>(converted), "Conversion Error");
}
