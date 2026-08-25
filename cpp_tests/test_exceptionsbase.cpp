#include <gtest/gtest.h>

#include "exceptionsbase.h"

// Test GenericErrorBase
TEST(ExceptionsBaseTest, GenericErrorBasicConstruction) {
   GenericErrorBase error("Test error message");
   EXPECT_STREQ(error.what(), "Test error message");
}

TEST(ExceptionsBaseTest, GenericErrorEmptyMessage) {
   GenericErrorBase error("");
   EXPECT_STREQ(error.what(), "");
}

TEST(ExceptionsBaseTest, GenericErrorThrow) {
   EXPECT_THROW({ throw GenericErrorBase("Test throw"); }, GenericErrorBase);
}

// Test ConnectionErrorBase
TEST(ExceptionsBaseTest, ConnectionErrorConstruction) {
   ConnectionErrorBase error("Connection failed");
   EXPECT_STREQ(error.what(), "Connection failed");
}

TEST(ExceptionsBaseTest, ConnectionErrorInheritance) {
   EXPECT_THROW({ throw ConnectionErrorBase("Connection error"); }, GenericErrorBase);
}

// Test TimeoutErrorBase
TEST(ExceptionsBaseTest, TimeoutErrorConstruction) {
   TimeoutErrorBase error("Request timed out");
   EXPECT_STREQ(error.what(), "Request timed out");
}

TEST(ExceptionsBaseTest, TimeoutErrorInheritance) {
   EXPECT_THROW({ throw TimeoutErrorBase("Timeout occurred"); }, GenericErrorBase);
}

// Test UnknownObjectIDErrorBase
TEST(ExceptionsBaseTest, UnknownObjectIDErrorConstruction) {
   UnknownObjectIDErrorBase error("Unknown OID");
   EXPECT_STREQ(error.what(), "Unknown OID");
}

TEST(ExceptionsBaseTest, UnknownObjectIDErrorInheritance) {
   EXPECT_THROW({ throw UnknownObjectIDErrorBase("OID not found"); }, GenericErrorBase);
}

// Test NoSuchNameErrorBase
TEST(ExceptionsBaseTest, NoSuchNameErrorConstruction) {
   NoSuchNameErrorBase error("No such name");
   EXPECT_STREQ(error.what(), "No such name");
}

TEST(ExceptionsBaseTest, NoSuchNameErrorInheritance) {
   EXPECT_THROW({ throw NoSuchNameErrorBase("Name not found"); }, GenericErrorBase);
}

// Test NoSuchObjectErrorBase
TEST(ExceptionsBaseTest, NoSuchObjectErrorConstruction) {
   NoSuchObjectErrorBase error("No such object");
   EXPECT_STREQ(error.what(), "No such object");
}

TEST(ExceptionsBaseTest, NoSuchObjectErrorInheritance) {
   EXPECT_THROW({ throw NoSuchObjectErrorBase("Object not available"); }, GenericErrorBase);
}

// Test NoSuchInstanceErrorBase
TEST(ExceptionsBaseTest, NoSuchInstanceErrorConstruction) {
   NoSuchInstanceErrorBase error("No such instance");
   EXPECT_STREQ(error.what(), "No such instance");
}

TEST(ExceptionsBaseTest, NoSuchInstanceErrorInheritance) {
   EXPECT_THROW({ throw NoSuchInstanceErrorBase("Instance not found"); }, GenericErrorBase);
}

// Test UndeterminedTypeErrorBase
TEST(ExceptionsBaseTest, UndeterminedTypeErrorConstruction) {
   UndeterminedTypeErrorBase error("Type undetermined");
   EXPECT_STREQ(error.what(), "Type undetermined");
}

TEST(ExceptionsBaseTest, UndeterminedTypeErrorInheritance) {
   EXPECT_THROW({ throw UndeterminedTypeErrorBase("Cannot determine type"); }, GenericErrorBase);
}

// Test ParseErrorBase
TEST(ExceptionsBaseTest, ParseErrorConstruction) {
   ParseErrorBase error("Parse error occurred");
   EXPECT_STREQ(error.what(), "Parse error occurred");
}

TEST(ExceptionsBaseTest, ParseErrorInheritance) {
   EXPECT_THROW({ throw ParseErrorBase("Failed to parse"); }, GenericErrorBase);
}

// Test PacketErrorBase
TEST(ExceptionsBaseTest, PacketErrorConstruction) {
   PacketErrorBase error("Packet error");
   EXPECT_STREQ(error.what(), "Packet error");
}

TEST(ExceptionsBaseTest, PacketErrorInheritance) {
   EXPECT_THROW({ throw PacketErrorBase("Malformed packet"); }, GenericErrorBase);
}

// Test catching specific exception types
TEST(ExceptionsBaseTest, CatchSpecificExceptionType) {
   try {
      throw ConnectionErrorBase("Connection failed");
      FAIL() << "Should have thrown exception";
   } catch (ConnectionErrorBase const& e) {
      EXPECT_STREQ(e.what(), "Connection failed");
   } catch (...) {
      FAIL() << "Caught wrong exception type";
   }
}

// Test catching as base class
TEST(ExceptionsBaseTest, CatchAsBaseClass) {
   try {
      throw TimeoutErrorBase("Timeout");
      FAIL() << "Should have thrown exception";
   } catch (GenericErrorBase const& e) {
      EXPECT_STREQ(e.what(), "Timeout");
   }
}

// Test exception message with special characters
TEST(ExceptionsBaseTest, SpecialCharactersInMessage) {
   GenericErrorBase error("Error: \n\t Special chars: !@#$%^&*()");
   EXPECT_STREQ(error.what(), "Error: \n\t Special chars: !@#$%^&*()");
}

// Test long error message
TEST(ExceptionsBaseTest, LongErrorMessage) {
   std::string long_msg(1000, 'A');
   GenericErrorBase error(long_msg);
   EXPECT_EQ(std::string(error.what()), long_msg);
}

// Test exception with multiline message
TEST(ExceptionsBaseTest, MultilineErrorMessage) {
   std::string multiline = "Line 1\nLine 2\nLine 3";
   PacketErrorBase error(multiline);
   EXPECT_STREQ(error.what(), multiline.c_str());
}

// Verify every exception type is catchable as std::exception
TEST(ExceptionsBaseTest, AllTypesInheritFromStdException) {
   EXPECT_THROW({ throw GenericErrorBase("x"); }, std::exception);
   EXPECT_THROW({ throw ConnectionErrorBase("x"); }, std::exception);
   EXPECT_THROW({ throw TimeoutErrorBase("x"); }, std::exception);
   EXPECT_THROW({ throw PacketErrorBase("x"); }, std::exception);
   EXPECT_THROW({ throw ParseErrorBase("x"); }, std::exception);
   EXPECT_THROW({ throw UnknownObjectIDErrorBase("x"); }, std::exception);
   EXPECT_THROW({ throw NoSuchNameErrorBase("x"); }, std::exception);
   EXPECT_THROW({ throw NoSuchObjectErrorBase("x"); }, std::exception);
   EXPECT_THROW({ throw NoSuchInstanceErrorBase("x"); }, std::exception);
   EXPECT_THROW({ throw UndeterminedTypeErrorBase("x"); }, std::exception);
}

// Verify each specific type can be caught by its own type
TEST(ExceptionsBaseTest, ParseErrorCaughtByOwnType) {
   try {
      throw ParseErrorBase("parse failure");
      FAIL() << "Expected ParseErrorBase";
   } catch (ParseErrorBase const& e) {
      EXPECT_STREQ(e.what(), "parse failure");
   } catch (...) {
      FAIL() << "Caught wrong type";
   }
}

TEST(ExceptionsBaseTest, PacketErrorCaughtByOwnType) {
   try {
      throw PacketErrorBase("bad packet");
      FAIL() << "Expected PacketErrorBase";
   } catch (PacketErrorBase const& e) {
      EXPECT_STREQ(e.what(), "bad packet");
   } catch (...) {
      FAIL() << "Caught wrong type";
   }
}
