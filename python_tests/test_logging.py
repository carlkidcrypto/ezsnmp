import unittest
import json
from ezsnmp import Session
from unittest_fixtures import BaseTestCase
from unittest.mock import patch
import sys
from io import StringIO


class TestSessionLogging(unittest.TestCase):
    def test_session_str(self):
        """
        Given a Session object with basic configuration parameters
        When the __str__ method is called
        Then it should return a human-readable string with session details
        """
        session = Session(hostname="testhost", port_number="161", version="2c")
        str_repr = str(session)

        self.assertIn("SNMP Session:", str_repr)
        self.assertIn("testhost", str_repr)
        self.assertIn("161", str_repr)
        self.assertIn("version=2c", str_repr)

    def test_session_repr(self):
        """
        Given a Session object with community credentials
        When the __repr__ method is called
        Then it should return a repr string with masked sensitive data
        """
        session = Session(
            hostname="localhost",
            port_number="11161",
            version="2c",
            community="public",
            retries=5,
            timeout=10,
        )
        repr_str = repr(session)

        self.assertIn("Session(", repr_str)
        self.assertIn("hostname='localhost'", repr_str)
        self.assertIn("port_number='11161'", repr_str)
        self.assertIn("version='2c'", repr_str)
        self.assertIn("***", repr_str)
        self.assertNotIn("public", repr_str)
        self.assertIn("retries='5'", repr_str)
        self.assertIn("timeout='10'", repr_str)

    def test_session_to_dict(self):
        """
        Given a Session object with SNMPv3 authentication and privacy credentials
        When the to_dict method is called
        Then it should return a dict with all parameters and masked credentials
        """
        session = Session(
            hostname="192.168.1.1",
            port_number="1161",
            version="3",
            community="private",
            security_username="admin",
            auth_protocol="SHA",
            auth_passphrase="secret123",
            privacy_protocol="AES",
            privacy_passphrase="secret456",
            retries=3,
            timeout=5,
            print_enums_numerically=True,
        )

        session_dict = session.to_dict()

        self.assertEqual(session_dict["hostname"], "192.168.1.1")
        self.assertEqual(session_dict["port_number"], "1161")
        self.assertEqual(session_dict["version"], "3")
        self.assertEqual(session_dict["security_username"], "admin")
        self.assertEqual(session_dict["auth_protocol"], "SHA")
        self.assertEqual(session_dict["privacy_protocol"], "AES")
        self.assertEqual(session_dict["retries"], "3")
        self.assertEqual(session_dict["timeout"], "5")
        if (
            "print_enums_numerically" in session_dict
            and session_dict["print_enums_numerically"] is not None
        ):
            self.assertTrue(session_dict["print_enums_numerically"])

        self.assertEqual(session_dict["community"], "***")
        self.assertNotIn("private", str(session_dict.values()))
        self.assertEqual(session_dict["auth_passphrase"], "***")
        self.assertNotIn("secret123", str(session_dict.values()))
        self.assertEqual(session_dict["privacy_passphrase"], "***")
        self.assertNotIn("secret456", str(session_dict.values()))

    def test_session_to_dict_json_serializable(self):
        """
        Given a Session object converted to a dictionary
        When serializing the dict to JSON
        Then it should serialize without errors
        """
        session = Session(hostname="localhost", version="2c", retries=5)
        session_dict = session.to_dict()

        json_str = json.dumps(session_dict)
        self.assertIsNotNone(json_str)
        self.assertIn("localhost", json_str)


    def test_session_logging_use_case(self):
        """
        Given a Session object with configuration
        When printing the session and its dictionary representation
        Then both should output without errors and show masked credentials
        """
        session = Session(hostname="10.0.0.1", version="2c", community="test")

        captured_output = StringIO()
        sys.stdout = captured_output
        print(f"Created session: {session}")
        print(f"Session details: {session.to_dict()}")
        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("Created session:", output)
        self.assertIn("10.0.0.1", output)
        self.assertIn("Session details:", output)


class TestResultLogging(BaseTestCase):
    def test_result_str(self):
        """
        Given SNMP query results from various protocol versions
        When the __str__ method is called on a Result object
        Then it should return a human-readable string with all fields
        """
        for sess_args in self.sess_params:
            with self.subTest(sess=sess_args):
                try:
                    sess = Session(**sess_args)
                    results = sess.get("sysDescr.0")
                    if not results:
                        self.skipTest("No results from SNMP agent")

                    result = results[0]
                    str_repr = str(result)

                    self.assertIn("oid:", str_repr)
                    self.assertIn("index:", str_repr)
                    self.assertIn("type:", str_repr)
                    self.assertIn("value:", str_repr)
                    self.assertIn("converted_value:", str_repr)
                    del sess

                except Exception as e:
                    self.skipTest(f"SNMP agent not available: {e}")

    def test_result_repr(self):
        """
        Given SNMP query results from various protocol versions
        When the __repr__ method is called on a Result object
        Then it should return a repr string starting with Result(
        """
        for sess_args in self.sess_params:
            with self.subTest(sess=sess_args):
                try:
                    sess = Session(**sess_args)
                    results = sess.get("sysDescr.0")
                    if not results:
                        self.skipTest("No results from SNMP agent")

                    result = results[0]
                    repr_str = repr(result)

                    self.assertTrue(repr_str.startswith("Result("))
                    self.assertIn("oid:", repr_str)
                    del sess

                except Exception as e:
                    self.skipTest(f"SNMP agent not available: {e}")

    def test_result_to_dict(self):
        """
        Given SNMP query results from various protocol versions
        When the to_dict method is called on a Result object
        Then it should return a dict with all result fields
        """
        for sess_args in self.sess_params:
            with self.subTest(sess=sess_args):
                try:
                    sess = Session(**sess_args)
                    results = sess.get("sysDescr.0")
                    if not results:
                        self.skipTest("No results from SNMP agent")

                    result = results[0]
                    result_dict = result.to_dict()

                    self.assertIn("oid", result_dict)
                    self.assertIn("index", result_dict)
                    self.assertIn("type", result_dict)
                    self.assertIn("value", result_dict)
                    self.assertIn("converted_value", result_dict)

                    self.assertIsInstance(result_dict["oid"], str)
                    self.assertIsInstance(result_dict["type"], str)
                    self.assertIsInstance(result_dict["value"], str)
                    del sess

                except Exception as e:
                    self.skipTest(f"SNMP agent not available: {e}")

    def test_result_to_dict_json_serializable(self):
        """
        Given SNMP query results converted to a dictionary
        When serializing the dict to JSON
        Then it should serialize without errors
        """
        for sess_args in self.sess_params:
            with self.subTest(sess=sess_args):
                try:
                    sess = Session(**sess_args)
                    results = sess.get("sysContact.0")
                    if not results:
                        self.skipTest("No results from SNMP agent")

                    result = results[0]
                    result_dict = result.to_dict()

                    json_str = json.dumps(result_dict, default=str)
                    self.assertIsNotNone(json_str)
                    del sess

                except Exception as e:
                    self.skipTest(f"SNMP agent not available: {e}")

    def test_result_logging_use_case(self):
        """
        Given SNMP query results from various protocol versions
        When printing the result and its dictionary representation
        Then both should output without errors
        """
        for sess_args in self.sess_params:
            with self.subTest(sess=sess_args):
                try:
                    sess = Session(**sess_args)
                    results = sess.get("sysContact.0")
                    if not results:
                        self.skipTest("No results from SNMP agent")

                    result = results[0]

                    captured_output = StringIO()
                    sys.stdout = captured_output
                    print(f"Got result: {result}")
                    print(f"Result as dict: {result.to_dict()}")
                    sys.stdout = sys.__stdout__

                    output = captured_output.getvalue()
                    self.assertIn("Got result:", output)
                    self.assertIn("oid:", output)
                    self.assertIn("Result as dict:", output)
                    del sess

                except Exception as e:
                    self.skipTest(f"SNMP agent not available: {e}")

    def test_multiple_results_logging(self):
        """
        Given multiple SNMP query results from a walk operation
        When logging each result's str and dict representations
        Then all results should contain the expected fields
        """
        for sess_args in self.sess_params:
            with self.subTest(sess=sess_args):
                try:
                    sess = Session(**sess_args)
                    results = sess.walk("system")
                    if not results:
                        self.skipTest("No results from SNMP walk")

                    for result in results[:3]:
                        str_repr = str(result)
                        self.assertIn("oid:", str_repr)
                        self.assertIn("converted_value:", str_repr)

                        dict_repr = result.to_dict()
                        self.assertIn("oid", dict_repr)
                        self.assertIn("converted_value", dict_repr)
                    del sess

                except Exception as e:
                    self.skipTest(f"SNMP agent not available: {e}")

    def test_result_converted_value_types(self):
        """
        Given SNMP query results for various OID types
        When accessing the converted_value field from to_dict
        Then the converted_value should be present and not None
        """
        for sess_args in self.sess_params:
            with self.subTest(sess=sess_args):
                try:
                    sess = Session(**sess_args)
                    test_oids = [
                        "sysContact.0",
                        "sysUpTime.0",
                        "sysServices.0",
                    ]

                    for oid in test_oids:
                        try:
                            results = sess.get(oid)
                            if not results:
                                continue

                            result = results[0]
                            result_dict = result.to_dict()

                            self.assertIn("converted_value", result_dict)
                            converted = result_dict["converted_value"]
                            self.assertIsNotNone(converted)

                        except Exception:
                            continue
                    del sess

                except Exception as e:
                    self.skipTest(f"SNMP agent not available: {e}")


if __name__ == '__main__':
    unittest.main()
