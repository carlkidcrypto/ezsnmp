"""
Network tests for Session.bulk_get operations.
"""

import pytest

from ezsnmp.exceptions import PacketError, TimeoutError
import faulthandler

faulthandler.enable()


def test_session_bulk_get(sess):

    if sess.version == "1":
        with pytest.raises(PacketError):
            sess.bulk_get(
                [
                    "sysUpTime",
                    "sysORLastChange",
                    "sysORID",
                    "sysORDescr",
                    "sysORUpTime",
                ],
            )
    else:
        res = sess.bulk_get(
            ["sysUpTime", "sysORLastChange", "sysORID", "sysORDescr", "sysORUpTime"]
        )

        # Checking if "sysUpTimeInstance" is in "oid" is enough. The preamble
        # changes per OS system
        # "DISMAN-EVENT-MIB::sysUpTimeInstance" MacOS
        # "DISMAN-EXPRESSION-MIB::sysUpTimeInstance" Linux
        assert "sysUpTimeInstance" in res[0].oid
        assert res[0].index == ""
        assert res[0].type == "Timeticks"

        assert res[4].oid == "SNMPv2-MIB::sysORUpTime"
        assert res[4].index == "1"
        assert res[4].type == "Timeticks"

        del sess


def test_session_bulk_get_none_oids(sess):
    """Test that Session.bulk_get(None) is treated same as empty list."""
    if sess.version == "1":
        with pytest.raises(PacketError):
            sess.bulk_get(None)
    else:
        res = sess.bulk_get(None)
        assert res is not None


def test_session_bulk_get_single_oid_string(sess):
    if sess.version == "1":
        pytest.skip("BULK GET is not supported in SNMPv1")
    try:
        res = sess.bulk_get(".1.3.6.1.2.1.1.5.0")
    except TimeoutError:
        pytest.skip("SNMP agent is not reachable in this environment")

    assert len(res) >= 1
    assert res[0].oid
    assert res[0].type
