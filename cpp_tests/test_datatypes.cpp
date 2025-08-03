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

// Helper function to create and test a Result object
void testResultConversion(const std::string& oid, const std::string& index,
                          const std::string& type, const std::string& value,
                          const std::string& expected_string,
                          const Result::ConvertedValue& expected_converted_value) {
    Result r;
    r.oid = oid;
    r.index = index;
    r.type = type;
    r.value = value;
    r.update_converted_value();

    EXPECT_EQ(r._to_string(), expected_string);

    // Use std::visit to compare the variant types and values
    std::visit([&](auto&& arg) {
        using T = std::decay_t<decltype(arg)>;
        if constexpr (std::is_same_v<T, int>) {
            EXPECT_EQ(arg, std::get<int>(expected_converted_value));
        } else if constexpr (std::is_same_v<T, uint32_t>) {
            EXPECT_EQ(arg, std::get<uint32_t>(expected_converted_value));
        } else if constexpr (std::is_same_v<T, uint64_t>) {
            EXPECT_EQ(arg, std::get<uint64_t>(expected_converted_value));
        } else if constexpr (std::is_same_v<T, std::string>) {
            EXPECT_EQ(arg, std::get<std::string>(expected_converted_value));
        } else if constexpr (std::is_same_v<T, std::vector<unsigned char>>) {
            EXPECT_EQ(arg, std::get<std::vector<unsigned char>>(expected_converted_value));
        } else {
            FAIL() << "Unsupported variant type in testResultConversion for comparison.";
        }
    }, r.converted_value);
}

// Test fixture for accessing private members of Result
class ResultConvertedValueTest : public ::testing::Test {
  protected:
   Result result_obj;
};

// Original tests (kept for completeness)
TEST_F(ResultConvertedValueTest, HandlesInteger) {
   auto converted = result_obj._make_converted_value("INTEGER", "4");
   EXPECT_EQ(std::get<int>(converted), 4);
}

TEST_F(ResultConvertedValueTest, HandlesCounter32) {
   auto converted = result_obj._make_converted_value("Counter32", "1738754");
   EXPECT_EQ(std::get<uint32_t>(converted), 1738754);
}

TEST_F(ResultConvertedValueTest, HandlesCounter64) {
   auto converted = result_obj._make_converted_value("Counter64", "22711");
   EXPECT_EQ(std::get<uint64_t>(converted), 22711);
}

TEST_F(ResultConvertedValueTest, HandlesTimeticks) {
   auto converted = result_obj._make_converted_value("Timeticks", "(3410517) 9:28:25.17");
   EXPECT_EQ(std::get<uint32_t>(converted), 3410517);
}

TEST_F(ResultConvertedValueTest, HandlesTimeticksAsInteger) {
   auto converted = result_obj._make_converted_value("Timeticks", "3410517");
   EXPECT_EQ(std::get<uint32_t>(converted), 3410517);
}

TEST_F(ResultConvertedValueTest, HandlesGauge32) {
   auto converted = result_obj._make_converted_value("Gauge32", "10000000");
   EXPECT_EQ(std::get<uint32_t>(converted), 10000000);
}

TEST_F(ResultConvertedValueTest, HandlesHexString) {
   auto converted = result_obj._make_converted_value("Hex-STRING", "00 15 5D 6E 34 05");
   std::vector<unsigned char> expected = {0x00, 0x15, 0x5D, 0x6E, 0x34, 0x05};
   EXPECT_EQ(std::get<std::vector<unsigned char>>(converted), expected);
}

TEST_F(ResultConvertedValueTest, HandlesString) {
   auto converted = result_obj._make_converted_value("STRING", "Some long string value");
   // Now returns the actual string value
   EXPECT_EQ(std::get<std::string>(converted), "Some long string value");
}

TEST_F(ResultConvertedValueTest, HandlesOid) {
   auto converted =
       result_obj._make_converted_value("OID", "SNMP-FRAMEWORK-MIB::snmpFrameworkMIBCompliance");
   // Now returns the actual OID string
   EXPECT_EQ(std::get<std::string>(converted), "SNMP-FRAMEWORK-MIB::snmpFrameworkMIBCompliance");
}

TEST_F(ResultConvertedValueTest, HandlesIpAddress) {
   auto converted = result_obj._make_converted_value("IpAddress", "172.25.10.171");
   // Now returns the actual IP address string
   EXPECT_EQ(std::get<std::string>(converted), "172.25.10.171");
}

TEST_F(ResultConvertedValueTest, HandlesInvalidInteger) {
   auto converted = result_obj._make_converted_value("INTEGER", "not-a-number");
   EXPECT_EQ(std::get<std::string>(converted), "INTEGER Conversion Error: stoi");
}

// --- New Tests for Various SNMP Types and Edge Cases ---

TEST_F(ResultConvertedValueTest, HandlesZeroTimeticks) {
   auto converted = result_obj._make_converted_value("Timeticks", "(0) 0:00:00.00");
   EXPECT_EQ(std::get<uint32_t>(converted), 0);
}

TEST_F(ResultConvertedValueTest, HandlesNegativeIntegerString) {
   auto converted = result_obj._make_converted_value("INTEGER", "-42");
   EXPECT_EQ(std::get<int>(converted), -42);
}

TEST_F(ResultConvertedValueTest, HandlesIntegerWithText) {
   auto converted = result_obj._make_converted_value("INTEGER", "up(1)");
   // Now it should successfully parse the '1'
   EXPECT_EQ(std::get<int>(converted), 1);
}

TEST_F(ResultConvertedValueTest, HandlesIntegerWithOtherText) {
   auto converted = result_obj._make_converted_value("INTEGER", "running(2)");
   // Now it should successfully parse the '2'
   EXPECT_EQ(std::get<int>(converted), 2);
}

TEST_F(ResultConvertedValueTest, HandlesNetworkAddress) {
   // Now handled specifically to return the string value
   auto converted = result_obj._make_converted_value("Network Address", "AC:19:00:01");
   EXPECT_EQ(std::get<std::string>(converted), "AC:19:00:01");
}

TEST_F(ResultConvertedValueTest, HandlesUnknownType) {
   auto converted = result_obj._make_converted_value("SOME-UNKNOWN-TYPE", "some value");
   EXPECT_EQ(std::get<std::string>(converted), "Unknown Type Conversion");
}

TEST_F(ResultConvertedValueTest, HandlesEmptyValueWithNumericType) {
   auto converted = result_obj._make_converted_value("INTEGER", "");
   // Updated error message for clarity
   EXPECT_EQ(std::get<std::string>(converted),
             "INTEGER Conversion Error: Empty value for numeric type");
}

TEST_F(ResultConvertedValueTest, HandlesEmptyValueWithHexString) {
   auto converted = result_obj._make_converted_value("Hex-STRING", "");
   std::vector<unsigned char> expected = {};
   EXPECT_EQ(std::get<std::vector<unsigned char>>(converted), expected);
}

TEST_F(ResultConvertedValueTest, HandlesEmptyValueWithString) {
   auto converted = result_obj._make_converted_value("STRING", "");
   // Now returns the empty string itself
   EXPECT_EQ(std::get<std::string>(converted), "");
}

TEST_F(ResultConvertedValueTest, HandlesOidWithValueZeroDotZero) {
   auto converted = result_obj._make_converted_value("OID", "SNMPv2-SMI::zeroDotZero");
   // Now returns the OID string
   EXPECT_EQ(std::get<std::string>(converted), "SNMPv2-SMI::zeroDotZero");
}

TEST_F(ResultConvertedValueTest, HandlesGauge32WithUnit) {
   // Should now correctly parse the numeric part
   auto converted = result_obj._make_converted_value("Gauge32", "60000 milli-seconds");
   EXPECT_EQ(std::get<uint32_t>(converted), 60000);
}

TEST_F(ResultConvertedValueTest, HandlesZeroCounter32) {
   auto converted = result_obj._make_converted_value("Counter32", "0");
   EXPECT_EQ(std::get<uint32_t>(converted), 0);
}

TEST_F(ResultConvertedValueTest, HandlesZeroCounter64) {
   auto converted = result_obj._make_converted_value("Counter64", "0");
   EXPECT_EQ(std::get<uint64_t>(converted), 0);
}

TEST_F(ResultConvertedValueTest, HandlesEmptyHexCharacters) {
   auto converted = result_obj._make_converted_value("Hex-STRING", " ");
   std::vector<unsigned char> expected = {};
   EXPECT_EQ(std::get<std::vector<unsigned char>>(converted), expected);
}

TEST_F(ResultConvertedValueTest, HandlesMalformedHexCharacters) {
   auto converted = result_obj._make_converted_value("Hex-STRING", "0xG");
   // Now returns an error string for malformed hex
   EXPECT_EQ(std::get<std::string>(converted),
             "Hex-STRING Conversion Error: Malformed hex part 'G'");
}

TEST_F(ResultConvertedValueTest, HandlesIpAddressConversionError) {
   // IpAddress now returns the original string, so no conversion error in this case
   auto converted = result_obj._make_converted_value("IpAddress", "invalid.ip.address");
   EXPECT_EQ(std::get<std::string>(converted), "invalid.ip.address");
}

TEST_F(ResultConvertedValueTest, HandlesOctetString) {
   auto converted = result_obj._make_converted_value("OCTETSTR", "some raw bytes");
   // Now returns the actual string value
   EXPECT_EQ(std::get<std::string>(converted), "some raw bytes");
}

TEST_F(ResultConvertedValueTest, HandlesObjID) {
   auto converted = result_obj._make_converted_value("OBJID", "1.3.6.1.2.1.1.1.0");
   // Now returns the actual string value
   EXPECT_EQ(std::get<std::string>(converted), "1.3.6.1.2.1.1.1.0");
}

TEST_F(ResultConvertedValueTest, HandlesNullType) {
   auto converted = result_obj._make_converted_value("NULL", "");
   // Now returns the empty string for NULL
   EXPECT_EQ(std::get<std::string>(converted), "");
}

TEST_F(ResultConvertedValueTest, HandlesOtherType) {
   auto converted = result_obj._make_converted_value("Other", "some value");
   // Now returns the actual string value
   EXPECT_EQ(std::get<std::string>(converted), "some value");
}

// --- Integration Tests (using testResultConversion helper) ---

TEST(ResultIntegrationTest, SysDescr) {
   testResultConversion(
       "SNMPv2-MIB::sysDescr", "0", "STRING",
       "Linux carlkidcrypto-w 5.15.167.4-microsoft-standard-WSL2 #1 SMP Tue Nov 5 00:21:55 UTC "
       "2024 x86_64",
       "oid: SNMPv2-MIB::sysDescr, index: 0, type: STRING, value: Linux carlkidcrypto-w "
       "5.15.167.4-microsoft-standard-WSL2 #1 SMP Tue Nov 5 00:21:55 UTC 2024 x86_64",
       std::string("Linux carlkidcrypto-w 5.15.167.4-microsoft-standard-WSL2 #1 SMP Tue Nov 5 "
                   "00:21:55 UTC 2024 x86_64"));
}

TEST(ResultIntegrationTest, SysObjectID) {
   testResultConversion(
       "SNMPv2-MIB::sysObjectID", "0", "OID", "NET-SNMP-TC::linux",
       "oid: SNMPv2-MIB::sysObjectID, index: 0, type: OID, value: NET-SNMP-TC::linux",
       std::string("NET-SNMP-TC::linux"));
}

TEST(ResultIntegrationTest, SysUpTimeInstance) {
   testResultConversion("DISMAN-EXPRESSION-MIB::sysUpTimeInstance", "", "Timeticks",
                        "(3410517) 9:28:25.17",
                        "oid: DISMAN-EXPRESSION-MIB::sysUpTimeInstance, index: , type: Timeticks, "
                        "value: (3410517) 9:28:25.17",
                        static_cast<uint32_t>(3410517));
}

TEST(ResultIntegrationTest, IfNumber) {
   testResultConversion("IF-MIB::ifNumber", "0", "INTEGER", "4",
                        "oid: IF-MIB::ifNumber, index: 0, type: INTEGER, value: 4", 4);
}

TEST(ResultIntegrationTest, IfSpeedGauge32) {
   testResultConversion("IF-MIB::ifSpeed", "1", "Gauge32", "10000000",
                        "oid: IF-MIB::ifSpeed, index: 1, type: Gauge32, value: 10000000",
                        static_cast<uint32_t>(10000000));
}

TEST(ResultIntegrationTest, IfPhysAddressStringContainsHex) {
   // As per the snmpwalk output, the type is STRING, even if the value looks like hex.
   // So converted_value will be the string.
   testResultConversion(
       "IF-MIB::ifPhysAddress", "2", "STRING", "0:15:5d:5f:7b:84",
       "oid: IF-MIB::ifPhysAddress, index: 2, type: STRING, value: 0:15:5d:5f:7b:84",
       std::string("0:15:5d:5f:7b:84"));
   // Specific test for when the type IS Hex-STRING
   testResultConversion("RFC1213-MIB::atPhysAddress", "2.1.172.25.0.1", "Hex-STRING",
                        "00 15 5D 6E 34 05",
                        "oid: RFC1213-MIB::atPhysAddress, index: 2.1.172.25.0.1, type: Hex-STRING, "
                        "value: 00 15 5D 6E 34 05",
                        std::vector<unsigned char>{0x00, 0x15, 0x5D, 0x6E, 0x34, 0x05});
}

TEST(ResultIntegrationTest, IfAdminStatusIntegerWithText) {
   testResultConversion("IF-MIB::ifAdminStatus", "1", "INTEGER", "up(1)",
                        "oid: IF-MIB::ifAdminStatus, index: 1, type: INTEGER, value: up(1)",
                        1 // Expecting 1 after parsing
   );
}

TEST(ResultIntegrationTest, IfInOctetsCounter32) {
   testResultConversion("IF-MIB::ifInOctets", "1", "Counter32", "1738754",
                        "oid: IF-MIB::ifInOctets, index: 1, type: Counter32, value: 1738754",
                        static_cast<uint32_t>(1738754));
}

TEST(ResultIntegrationTest, IpSystemStatsHCInReceivesCounter64) {
   testResultConversion(
       "IP-MIB::ipSystemStatsHCInReceives", "ipv4", "Counter64", "22711",
       "oid: IP-MIB::ipSystemStatsHCInReceives, index: ipv4, type: Counter64, value: 22711",
       static_cast<uint64_t>(22711));
}

TEST(ResultIntegrationTest, IpAddressIpAddress) {
   testResultConversion(
       "RFC1213-MIB::ipAdEntAddr", "172.25.10.171", "IpAddress", "172.25.10.171",
       "oid: RFC1213-MIB::ipAdEntAddr, index: 172.25.10.171, type: IpAddress, value: 172.25.10.171",
       std::string("172.25.10.171"));
}

TEST(ResultIntegrationTest, TcpMaxConnNegativeInteger) {
   testResultConversion("RFC1213-MIB::tcpMaxConn", "0", "INTEGER", "-1",
                        "oid: RFC1213-MIB::tcpMaxConn, index: 0, type: INTEGER, value: -1", -1);
}

TEST(ResultIntegrationTest, HrSystemDateString) {
   testResultConversion("HOST-RESOURCES-MIB::hrSystemDate", "0", "STRING",
                        "2025-7-9,7:36:11.0,-7:0",
                        "oid: HOST-RESOURCES-MIB::hrSystemDate, index: 0, type: STRING, value: "
                        "2025-7-9,7:36:11.0,-7:0",
                        std::string("2025-7-9,7:36:11.0,-7:0"));
}

TEST(ResultIntegrationTest, HrMemorySizeInteger) {
   testResultConversion(
       "HOST-RESOURCES-MIB::hrMemorySize", "0", "INTEGER", "7965876",
       "oid: HOST-RESOURCES-MIB::hrMemorySize, index: 0, type: INTEGER, value: 7965876", 7965876);
}

TEST(ResultIntegrationTest, HrStorageAllocationUnitsIntegerWithUnit) {
   testResultConversion("HOST-RESOURCES-MIB::hrStorageAllocationUnits", "1", "INTEGER",
                        "1024 Bytes",
                        "oid: HOST-RESOURCES-MIB::hrStorageAllocationUnits, index: 1, type: "
                        "INTEGER, value: 1024 Bytes",
                        1024 // Expecting 1024 after parsing
   );
}

TEST(ResultIntegrationTest, HrDeviceStatusIntegerWithText) {
   testResultConversion(
       "HOST-RESOURCES-MIB::hrDeviceStatus", "196608", "INTEGER", "running(2)",
       "oid: HOST-RESOURCES-MIB::hrDeviceStatus, index: 196608, type: INTEGER, value: running(2)",
       2 // Expecting 2 after parsing
   );
}

TEST(ResultIntegrationTest, HrFSAccessIntegerWithText) {
   testResultConversion(
       "HOST-RESOURCES-MIB::hrFSAccess", "1", "INTEGER", "readWrite(1)",
       "oid: HOST-RESOURCES-MIB::hrFSAccess, index: 1, type: INTEGER, value: readWrite(1)",
       1 // Expecting 1 after parsing
   );
}

TEST(ResultIntegrationTest, IpAddressStorageTypeIntegerWithText) {
   testResultConversion("IP-MIB::ipAddressStorageType", "ipv4.\"10.255.255.254\"", "INTEGER",
                        "volatile(2)",
                        "oid: IP-MIB::ipAddressStorageType, index: ipv4.\"10.255.255.254\", type: "
                        "INTEGER, value: volatile(2)",
                        2 // Expecting 2 after parsing
   );
}

TEST(ResultIntegrationTest, IpSystemStatsRefreshRateGauge32WithUnit) {
   testResultConversion("IP-MIB::ipSystemStatsRefreshRate", "ipv4", "Gauge32",
                        "60000 milli-seconds",
                        "oid: IP-MIB::ipSystemStatsRefreshRate, index: ipv4, type: Gauge32, value: "
                        "60000 milli-seconds",
                        static_cast<uint32_t>(60000) // Expecting 60000 after parsing
   );
}

TEST(ResultIntegrationTest, IcmpMsgStatsInPktsCounter32) {
   testResultConversion("IP-MIB::icmpMsgStatsInPkts", "ipv4.0", "Counter32", "0",
                        "oid: IP-MIB::icmpMsgStatsInPkts, index: ipv4.0, type: Counter32, value: 0",
                        static_cast<uint32_t>(0));
}

TEST(ResultIntegrationTest, TcpRtoAlgorithmIntegerWithText) {
   testResultConversion(
       "RFC1213-MIB::tcpRtoAlgorithm", "0", "INTEGER", "other(1)",
       "oid: RFC1213-MIB::tcpRtoAlgorithm, index: 0, type: INTEGER, value: other(1)",
       1 // Expecting 1 after parsing
   );
}

TEST(ResultIntegrationTest, SnmpEnableAuthenTrapsIntegerWithText) {
   testResultConversion(
       "SNMPv2-MIB::snmpEnableAuthenTraps", "0", "INTEGER", "disabled(2)",
       "oid: SNMPv2-MIB::snmpEnableAuthenTraps, index: 0, type: INTEGER, value: disabled(2)",
       2 // Expecting 2 after parsing
   );
}

TEST(ResultIntegrationTest, HrSystemInitialLoadParametersStringWithQuotes) {
   testResultConversion(
       "HOST-RESOURCES-MIB::hrSystemInitialLoadParameters", "0", "STRING",
       "\"initrd=\\initrd.img WSL_ROOT_INIT=1 panic=-1 nr_cpus=12 hv_utils.timesync_implicit=1 "
       "console=hvc0 debug pty.legacy_count=0 WSL_EN\"",
       "oid: HOST-RESOURCES-MIB::hrSystemInitialLoadParameters, index: 0, type: STRING, value: "
       "\"initrd=\\initrd.img WSL_ROOT_INIT=1 panic=-1 nr_cpus=12 hv_utils.timesync_implicit=1 "
       "console=hvc0 debug pty.legacy_count=0 WSL_EN\"",
       std::string("\"initrd=\\initrd.img WSL_ROOT_INIT=1 panic=-1 nr_cpus=12 "
                   "hv_utils.timesync_implicit=1 console=hvc0 debug pty.legacy_count=0 WSL_EN\""));
}

TEST(ResultIntegrationTest, MissingDatatype) {
   Result r;
   r.oid = "test::oid";
   r.index = "1";
   r.type = ""; // Missing type
   r.value = "some value";
   r.update_converted_value();

   EXPECT_EQ(r._to_string(), "oid: test::oid, index: 1, type: , value: some value");
   EXPECT_EQ(std::get<std::string>(r.converted_value), "Unknown Type Conversion");
}

TEST(ResultIntegrationTest, UnhandledTypeNotRequiringConversion) {
   testResultConversion(
       "Some-MIB::octetString", "1", "OCTETSTR", "some raw bytes",
       "oid: Some-MIB::octetString, index: 1, type: OCTETSTR, value: some raw bytes",
       std::string("some raw bytes"));
}