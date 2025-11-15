import unittest
import faulthandler
from ezsnmp import Session
from ezsnmp.exceptions import (
    GenericError,
    ConnectionError,
    NoSuchInstanceError,
    NoSuchNameError,
    NoSuchObjectError,
    PacketError,
    ParseError,
    TimeoutError,
    UndeterminedTypeError,
    UnknownObjectIDError,
)

faulthandler.enable()


class TestExceptions(unittest.TestCase):
    def test_generic_error(self):
        """
        Given a GenericError exception class
        When the exception is raised with a message
        Then the exception should be raised and contain the message
        """
        with self.assertRaises(GenericError) as exc_info:
            raise GenericError("Test generic error")
        self.assertIn("Test generic error", str(exc_info.exception))

    def test_connection_error(self):
        """
        Given a ConnectionError exception class
        When the exception is raised with a message
        Then the exception should be raised and contain the message
        """
        with self.assertRaises(ConnectionError) as exc_info:
            raise ConnectionError("Test connection error")
        self.assertIn("Test connection error", str(exc_info.exception))

    def test_no_such_instance_error(self):
        """
        Given a NoSuchInstanceError exception class
        When the exception is raised with a message
        Then the exception should be raised and contain the message
        """
        with self.assertRaises(NoSuchInstanceError) as exc_info:
            raise NoSuchInstanceError("Test no such instance error")
        self.assertIn("Test no such instance error", str(exc_info.exception))

    def test_no_such_name_error(self):
        """
        Given a NoSuchNameError exception class
        When the exception is raised with a message
        Then the exception should be raised and contain the message
        """
        with self.assertRaises(NoSuchNameError) as exc_info:
            raise NoSuchNameError("Test no such name error")
        self.assertIn("Test no such name error", str(exc_info.exception))

    def test_no_such_object_error(self):
        """
        Given a NoSuchObjectError exception class
        When the exception is raised with a message
        Then the exception should be raised and contain the message
        """
        with self.assertRaises(NoSuchObjectError) as exc_info:
            raise NoSuchObjectError("Test no such object error")
        self.assertIn("Test no such object error", str(exc_info.exception))

    def test_packet_error(self):
        """
        Given a PacketError exception class
        When the exception is raised with a message
        Then the exception should be raised and contain the message
        """
        with self.assertRaises(PacketError) as exc_info:
            raise PacketError("Test packet error")
        self.assertIn("Test packet error", str(exc_info.exception))

    def test_parse_error(self):
        """
        Given a ParseError exception class
        When the exception is raised with a message
        Then the exception should be raised and contain the message
        """
        with self.assertRaises(ParseError) as exc_info:
            raise ParseError("Test parse error")
        self.assertIn("Test parse error", str(exc_info.exception))

    def test_timeout_error(self):
        """
        Given a TimeoutError exception class
        When the exception is raised with a message
        Then the exception should be raised and contain the message
        """
        with self.assertRaises(TimeoutError) as exc_info:
            raise TimeoutError("Test timeout error")
        self.assertIn("Test timeout error", str(exc_info.exception))

    def test_undetermined_type_error(self):
        """
        Given an UndeterminedTypeError exception class
        When the exception is raised with a message
        Then the exception should be raised and contain the message
        """
        with self.assertRaises(UndeterminedTypeError) as exc_info:
            raise UndeterminedTypeError("Test undetermined type error")
        self.assertIn("Test undetermined type error", str(exc_info.exception))

    def test_unknown_object_id_error(self):
        """
        Given an UnknownObjectIDError exception class
        When the exception is raised with a message
        Then the exception should be raised and contain the message
        """
        with self.assertRaises(UnknownObjectIDError) as exc_info:
            raise UnknownObjectIDError("Test unknown object ID error")
        self.assertIn("Test unknown object ID error", str(exc_info.exception))


if __name__ == '__main__':
    unittest.main()
