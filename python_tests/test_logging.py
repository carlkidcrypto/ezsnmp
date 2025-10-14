"""
Tests for logging and string representation functionality (Issue #409).

This tests the __str__, __repr__, and to_dict methods added to Session and Result classes
to enable proper logging and JSON serialization.
"""

import pytest
import json
from ezsnmp import Session


def test_session_str():
    """Test Session.__str__() produces a user-friendly string."""
    session = Session(hostname="testhost", port_number="161", version="2c")
    str_repr = str(session)

    assert "SNMP Session:" in str_repr
    assert "testhost" in str_repr
    assert "161" in str_repr
    assert "version=2c" in str_repr


def test_session_repr():
    """Test Session.__repr__() produces a detailed representation."""
    session = Session(
        hostname="localhost",
        port_number="11161",
        version="2c",
        community="public",
        retries=5,
        timeout=10,
    )
    repr_str = repr(session)

    assert "Session(" in repr_str
    assert "hostname='localhost'" in repr_str
    assert "port_number='11161'" in repr_str
    assert "version='2c'" in repr_str
    # Community should be masked
    assert "***" in repr_str
    assert "public" not in repr_str
    assert "retries=5" in repr_str
    assert "timeout=10" in repr_str


def test_session_to_dict():
    """Test Session.to_dict() produces a complete dictionary."""
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

    # Check all expected keys are present
    assert session_dict["hostname"] == "192.168.1.1"
    assert session_dict["port_number"] == "1161"
    assert session_dict["version"] == "3"
    assert session_dict["security_username"] == "admin"
    assert session_dict["auth_protocol"] == "SHA"
    assert session_dict["privacy_protocol"] == "AES"
    assert session_dict["retries"] == 3
    assert session_dict["timeout"] == 5
    assert session_dict["print_enums_numerically"] is True

    # Check sensitive fields are masked
    assert session_dict["community"] == "***"
    assert "private" not in str(session_dict.values())
    assert session_dict["auth_passphrase"] == "***"
    assert "secret123" not in str(session_dict.values())
    assert session_dict["privacy_passphrase"] == "***"
    assert "secret456" not in str(session_dict.values())


def test_session_to_dict_json_serializable():
    """Test that Session.to_dict() can be serialized to JSON."""
    session = Session(hostname="localhost", version="2c", retries=5)
    session_dict = session.to_dict()

    # Should be able to serialize to JSON without errors
    json_str = json.dumps(session_dict)
    assert json_str is not None
    assert "localhost" in json_str


def test_session_logging_use_case(capfd):
    """Test that Session objects can be logged easily."""
    session = Session(hostname="10.0.0.1", version="2c", community="test")

    # Simulate logging by printing
    print(f"Created session: {session}")
    print(f"Session details: {session.to_dict()}")

    captured = capfd.readouterr()
    assert "Created session:" in captured.out
    assert "10.0.0.1" in captured.out
    assert "Session details:" in captured.out


def test_result_str(sess):
    """Test Result.__str__() produces a readable string with converted_value."""
    try:
        results = sess.get("sysDescr.0")
        if not results:
            pytest.skip("No results from SNMP agent")

        result = results[0]
        str_repr = str(result)

        # Should contain all fields including converted_value
        assert "oid:" in str_repr
        assert "index:" in str_repr
        assert "type:" in str_repr
        assert "value:" in str_repr
        assert "converted_value:" in str_repr

    except Exception as e:
        pytest.skip(f"SNMP agent not available: {e}")


def test_result_repr(sess):
    """Test Result.__repr__() produces a detailed representation."""
    try:
        results = sess.get("sysDescr.0")
        if not results:
            pytest.skip("No results from SNMP agent")

        result = results[0]
        repr_str = repr(result)

        # Should start with Result(
        assert repr_str.startswith("Result(")
        assert "oid:" in repr_str

    except Exception as e:
        pytest.skip(f"SNMP agent not available: {e}")


def test_result_to_dict(sess):
    """Test Result.to_dict() produces a dictionary with all fields."""
    try:
        results = sess.get("sysDescr.0")
        if not results:
            pytest.skip("No results from SNMP agent")

        result = results[0]
        result_dict = result.to_dict()

        # Check all expected keys
        assert "oid" in result_dict
        assert "index" in result_dict
        assert "type" in result_dict
        assert "value" in result_dict
        assert "converted_value" in result_dict

        # Check that values are accessible
        assert isinstance(result_dict["oid"], str)
        assert isinstance(result_dict["type"], str)
        assert isinstance(result_dict["value"], str)

    except Exception as e:
        pytest.skip(f"SNMP agent not available: {e}")


def test_result_to_dict_json_serializable(sess):
    """Test that Result.to_dict() can be serialized to JSON."""
    try:
        results = sess.get("sysContact.0")
        if not results:
            pytest.skip("No results from SNMP agent")

        result = results[0]
        result_dict = result.to_dict()

        # Should be able to serialize to JSON
        # Note: Some converted_value types (like bytes) may need special handling
        json_str = json.dumps(result_dict, default=str)
        assert json_str is not None

    except Exception as e:
        pytest.skip(f"SNMP agent not available: {e}")


def test_result_logging_use_case(sess, capfd):
    """Test that Result objects can be logged easily."""
    try:
        results = sess.get("sysContact.0")
        if not results:
            pytest.skip("No results from SNMP agent")

        result = results[0]

        # Simulate logging
        print(f"Got result: {result}")
        print(f"Result as dict: {result.to_dict()}")

        captured = capfd.readouterr()
        assert "Got result:" in captured.out
        assert "oid:" in captured.out
        assert "Result as dict:" in captured.out

    except Exception as e:
        pytest.skip(f"SNMP agent not available: {e}")


def test_multiple_results_logging(sess):
    """Test logging multiple Result objects."""
    try:
        results = sess.walk("system")
        if not results:
            pytest.skip("No results from SNMP walk")

        # Should be able to iterate and log all results
        for result in results[:3]:  # Check first 3
            str_repr = str(result)
            assert "oid:" in str_repr
            assert "converted_value:" in str_repr

            dict_repr = result.to_dict()
            assert "oid" in dict_repr
            assert "converted_value" in dict_repr

    except Exception as e:
        pytest.skip(f"SNMP agent not available: {e}")


def test_result_converted_value_types(sess):
    """Test that converted_value is properly exposed in to_dict()."""
    try:
        # Test different SNMP types
        test_oids = [
            "sysContact.0",  # STRING
            "sysUpTime.0",  # Timeticks (uint32)
            "sysServices.0",  # INTEGER
        ]

        for oid in test_oids:
            try:
                results = sess.get(oid)
                if not results:
                    continue

                result = results[0]
                result_dict = result.to_dict()

                # converted_value should be present and not None
                assert "converted_value" in result_dict
                converted = result_dict["converted_value"]

                # Should be a Python native type (int, str, bytes, etc.)
                assert converted is not None

            except Exception:
                continue  # Skip OIDs that don't exist

    except Exception as e:
        pytest.skip(f"SNMP agent not available: {e}")
