import platform

import pytest
from ezsnmp import (
    snmpget,
    snmpset,
    # snmpset_multiple,
    # snmpget_next,
    snmpbulkget,
    snmpwalk,
    snmpbulkwalk,
)


def test_snmp_get_regular(sess_args):
    res = snmpget("sysDescr.0", **sess_args)

    assert platform.version() in res.value
    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"


def test_snmp_get_tuple(sess_args):
    res = snmpget(("sysDescr", "0"), **sess_args)

    assert platform.version() in res.value
    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"


def test_snmp_get_fully_qualified(sess_args):
    res = snmpget(".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0", **sess_args)

    assert platform.version() in res.value
    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"


def test_snmp_get_fully_qualified_tuple(sess_args):
    res = snmpget(
        (".iso.org.dod.internet.mgmt.mib-2.system.sysDescr", "0"), **sess_args
    )

    assert platform.version() in res.value
    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"


def test_snmp_get_numeric(sess_args):
    res = snmpget(".1.3.6.1.2.1.1.1.0", **sess_args)

    assert platform.version() in res.value
    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"


def test_snmp_get_numeric_no_leading_dot(sess_args):
    res = snmpget("1.3.6.1.2.1.1.1.0", **sess_args)

    assert platform.version() in res.value
    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"


def test_snmp_get_numeric_tuple(sess_args):
    res = snmpget((".1.3.6.1.2.1.1.1", "0"), **sess_args)

    assert platform.version() in res.value
    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"


def test_snmp_get_unknown(sess_args):
    with pytest.raises():
        snmpget("sysDescripto.0", **sess_args)


def test_snmp_v1_get_with_retry_no_such(sess_args):
    res = snmpget(["iso", "sysDescr.0", "iso"], retry_no_such=True, **sess_args)

    assert res[0]
    if sess_args["version"] == 1:
        assert res[0].oid == "iso"
        assert res[0].snmp_type == "NOSUCHNAME"
    else:
        assert res[0].snmp_type == "NOSUCHOBJECT"

    assert res[1]
    assert platform.version() in res[1].value
    assert res[1].oid == "sysDescr"
    assert res[1].oid_index == "0"
    assert res[1].snmp_type == "OCTETSTR"

    assert res[2]
    if sess_args["version"] == 1:
        assert res[2].oid == "iso"
        assert res[2].snmp_type == "NOSUCHNAME"
    else:
        assert res[2].snmp_type == "NOSUCHOBJECT"


def test_snmp_get_invalid_instance(sess_args):
    # Sadly, SNMP v1 doesn't distuingish between an invalid instance and an
    # invalid object ID, instead it excepts with noSuchName
    if sess_args["version"] == 1:
        with pytest.raises():
            snmpget("sysContact.1", **sess_args)
    else:
        res = snmpget("sysContact.1", **sess_args)
        assert res.snmp_type == "NOSUCHINSTANCE"


def test_snmp_get_invalid_instance_with_abort_enabled(sess_args):
    # Sadly, SNMP v1 doesn't distuingish between an invalid instance and an
    # invalid object ID, so it raises the same exception for both
    if sess_args["version"] == 1:
        with pytest.raises():
            snmpget("sysContact.1", abort_on_nonexistent=True, **sess_args)
    else:
        with pytest.raises():
            snmpget("sysContact.1", abort_on_nonexistent=True, **sess_args)


def test_snmp_get_invalid_object(sess_args):
    if sess_args["version"] == 1:
        with pytest.raises():
            snmpget("iso", **sess_args)
    else:
        res = snmpget("iso", **sess_args)
        assert res.snmp_type == "NOSUCHOBJECT"


def test_snmp_get_invalid_object_with_abort_enabled(sess_args):
    if sess_args["version"] == 1:
        with pytest.raises():
            snmpget("iso", abort_on_nonexistent=True, **sess_args)
    else:
        with pytest.raises():
            snmpget("iso", abort_on_nonexistent=True, **sess_args)


def test_snmp_get_next(sess_args):
    res = snmp_get_next("nsCacheEntry", **sess_args)

    assert res.oid == "nsCacheTimeout"
    assert res.oid_index == "1.3.6.1.2.1.2.2"
    assert int(res.value) >= 0
    assert res.snmp_type == "INTEGER"


def test_snmp_get_next_numeric(sess_args):
    res = snmp_get_next((".1.3.6.1.2.1.1.1", "0"), **sess_args)

    assert res.oid == "sysObjectID"
    assert res.oid_index == "0"
    # .10 == Linux, .16 == macosx, .13 == win32, .255 == UNKNOWN
    assert res.value.rsplit(".", 1)[0] == ".1.3.6.1.4.1.8072.3.2"
    assert res.snmp_type == "OBJECTID"


def test_snmp_get_next_with_retry_no_such(sess_args):
    res = snmpget(["iso.9", "sysDescr.0", "iso.9"], retry_no_such=True, **sess_args)

    assert res[0]
    if sess_args["version"] == 1:
        assert res[0].value == "NOSUCHNAME"
        assert res[0].oid == "iso"
        assert res[0].oid_index == "9"
        assert res[0].snmp_type == "NOSUCHNAME"
    else:
        assert res[0].snmp_type == "NOSUCHOBJECT"

    assert res[1]
    assert platform.version() in res[1].value
    assert res[1].oid == "sysDescr"
    assert res[1].oid_index == "0"
    assert res[1].snmp_type == "OCTETSTR"

    assert res[2]
    if sess_args["version"] == 1:
        assert res[2].value == "NOSUCHNAME"
        assert res[2].oid == "iso"
        assert res[2].oid_index == "9"
        assert res[2].snmp_type == "NOSUCHNAME"
    else:
        assert res[2].snmp_type == "NOSUCHOBJECT"


def test_snmp_get_next_end_of_mib_view(sess_args):
    if sess_args["version"] == 1:
        with pytest.raises():
            snmp_get_next(["iso.9", "sysDescr", "iso.9"], **sess_args)
    else:
        res = snmp_get_next(["iso.9", "sysDescr", "iso.9"], **sess_args)

        assert res[0]
        assert res[0].value == "ENDOFMIBVIEW"
        assert res[0].oid == "iso.9"
        assert res[0].snmp_type == "ENDOFMIBVIEW"

        assert res[1]
        assert platform.version() in res[1].value
        assert res[1].oid == "sysDescr"
        assert res[1].oid_index == "0"
        assert res[1].snmp_type == "OCTETSTR"

        assert res[2]
        assert res[2].value == "ENDOFMIBVIEW"
        assert res[2].oid == "iso.9"
        assert res[2].snmp_type == "ENDOFMIBVIEW"


def test_snmp_get_next_unknown(sess_args):
    with pytest.raises():
        snmp_get_next("sysDescripto.0", **sess_args)


def test_snmp_set_string(sess_args, request, reset_values):
    res = snmpget(("sysLocation", "0"), **sess_args)
    assert res.oid == "sysLocation"
    assert res.oid_index == "0"
    assert res.value != "my newer location"
    assert res.snmp_type == "OCTETSTR"

    success = snmpset(("sysLocation", "0"), "my newer location", **sess_args)
    assert success

    res = snmpget(("sysLocation", "0"), **sess_args)
    assert res.oid == "sysLocation"
    assert res.oid_index == "0"
    assert res.value == "my newer location"
    assert res.snmp_type == "OCTETSTR"


def test_snmp_set_string_long_type(sess_args, reset_values):
    res = snmpget(("sysLocation", "0"), **sess_args)
    assert res.oid == "sysLocation"
    assert res.oid_index == "0"
    assert res.value != "my newer location"
    assert res.snmp_type == "OCTETSTR"

    success = snmpset(
        ("sysLocation", "0"), "my newer location", "OCTETSTR", **sess_args
    )
    assert success

    res = snmpget(("sysLocation", "0"), **sess_args)
    assert res.oid == "sysLocation"
    assert res.oid_index == "0"
    assert res.value == "my newer location"
    assert res.snmp_type == "OCTETSTR"


def test_snmp_set_string_short_type(sess_args, reset_values):
    res = snmpget(("sysLocation", "0"), **sess_args)
    assert res.oid == "sysLocation"
    assert res.oid_index == "0"
    assert res.value != "my newer location"
    assert res.snmp_type == "OCTETSTR"

    success = snmpset(("sysLocation", "0"), "my newer location", "s", **sess_args)
    assert success

    res = snmpget(("sysLocation", "0"), **sess_args)
    assert res.oid == "sysLocation"
    assert res.oid_index == "0"
    assert res.value == "my newer location"
    assert res.snmp_type == "OCTETSTR"


def test_snmp_set_integer(sess_args, reset_values):
    success = snmpset(("nsCacheTimeout", ".1.3.6.1.2.1.2.2"), 65, **sess_args)
    assert success

    res = snmpget(("nsCacheTimeout", ".1.3.6.1.2.1.2.2"), **sess_args)
    assert res.oid == "nsCacheTimeout"
    assert res.oid_index == "1.3.6.1.2.1.2.2"
    assert res.value == "65"
    assert res.snmp_type == "INTEGER"


def test_snmp_set_integer_long_type(sess_args, reset_values):
    success = snmpset(
        ("nsCacheTimeout", ".1.3.6.1.2.1.2.2"), 65, "INTEGER", **sess_args
    )
    assert success

    res = snmpget(("nsCacheTimeout", ".1.3.6.1.2.1.2.2"), **sess_args)
    assert res.oid == "nsCacheTimeout"
    assert res.oid_index == "1.3.6.1.2.1.2.2"
    assert res.value == "65"
    assert res.snmp_type == "INTEGER"


def test_snmp_set_integer_short_type(sess_args, reset_values):
    success = snmpset(("nsCacheTimeout", ".1.3.6.1.2.1.2.2"), 65, "i", **sess_args)
    assert success

    res = snmpget(("nsCacheTimeout", ".1.3.6.1.2.1.2.2"), **sess_args)
    assert res.oid == "nsCacheTimeout"
    assert res.oid_index == "1.3.6.1.2.1.2.2"
    assert res.value == "65"
    assert res.snmp_type == "INTEGER"


def test_snmp_set_unknown(sess_args):
    with pytest.raises():
        snmpset("nsCacheTimeoooout", 1234, **sess_args)


def test_snmp_set_multiple(sess_args, reset_values):
    res = snmpget(["sysLocation.0", "nsCacheTimeout.1.3.6.1.2.1.2.2"], **sess_args)
    assert res[0].value != "my newer location"
    assert res[1].value != "162"

    success = snmp_set_multiple(
        [
            ("sysLocation.0", "my newer location"),
            (("nsCacheTimeout", ".1.3.6.1.2.1.2.2"), 162),
        ],
        **sess_args
    )
    assert success

    res = snmpget(["sysLocation.0", "nsCacheTimeout.1.3.6.1.2.1.2.2"], **sess_args)
    assert res[0].value == "my newer location"
    assert res[1].value == "162"


def test_snmp_get_bulk(sess_args):
    if sess_args["version"] == 1:
        with pytest.raises():
            snmp_get_bulk(
                [
                    "sysUpTime",
                    "sysORLastChange",
                    "sysORID",
                    "sysORDescr",
                    "sysORUpTime",
                ],
                2,
                8,
                **sess_args
            )
    else:
        res = snmp_get_bulk(
            ["sysUpTime", "sysORLastChange", "sysORID", "sysORDescr", "sysORUpTime"],
            2,
            8,
            **sess_args
        )

        assert len(res) == 26

        assert res[0].oid == "sysUpTimeInstance"
        assert res[0].oid_index == ""
        assert int(res[0].value) > 0
        assert res[0].snmp_type == "TICKS"

        assert res[4].oid == "sysORUpTime"
        assert res[4].oid_index == "1"
        assert int(res[4].value) >= 0
        assert res[4].snmp_type == "TICKS"


def test_snmpwalk(sess_args):
    res = snmpwalk("system", **sess_args)
    assert len(res) >= 7

    assert platform.version() in res[0].value
    assert res[3].value == "G. S. Marzot <gmarzot@marzot.net>"
    assert res[4].value == platform.node()
    assert res[5].value == "my original location"


def test_snmp_walk_res(sess_args):
    res = snmpwalk("system", **sess_args)

    assert len(res) >= 7

    assert res[0].oid == "sysDescr"
    assert res[0].oid_index == "0"
    assert platform.version() in res[0].value
    assert res[0].snmp_type == "OCTETSTR"

    assert res[3].oid == "sysContact"
    assert res[3].oid_index == "0"
    assert res[3].value == "G. S. Marzot <gmarzot@marzot.net>"
    assert res[3].snmp_type == "OCTETSTR"

    assert res[4].oid == "sysName"
    assert res[4].oid_index == "0"
    assert res[4].value == platform.node()
    assert res[4].snmp_type == "OCTETSTR"

    assert res[5].oid == "sysLocation"
    assert res[5].oid_index == "0"
    assert res[5].value == "my original location"
    assert res[5].snmp_type == "OCTETSTR"


def test_snmp_walk_with_retry_no_such(sess_args):
    res = snmpwalk(["iso.9"], retry_no_such=True, **sess_args)
    # The above could trigger bug #162 as a PDU gets free'd by
    # the Net-SNMP library, but since it was not passed by ref,
    # it does not get set to NULL when leaving the function.
    assert res == []


def test_snmp_bulkwalk_res(sess_args):
    if sess_args["version"] == 1:
        with pytest.raises():
            snmpbulkwalk("system", **sess_args)
    else:
        res = snmpbulkwalk("system", **sess_args)

        assert len(res) >= 7

        assert res[0].oid == "sysDescr"
        assert res[0].oid_index == "0"
        assert platform.version() in res[0].value
        assert res[0].snmp_type == "OCTETSTR"

        assert res[3].oid == "sysContact"
        assert res[3].oid_index == "0"
        assert res[3].value == "G. S. Marzot <gmarzot@marzot.net>"
        assert res[3].snmp_type == "OCTETSTR"

        assert res[4].oid == "sysName"
        assert res[4].oid_index == "0"
        assert res[4].value == platform.node()
        assert res[4].snmp_type == "OCTETSTR"

        assert res[5].oid == "sysLocation"
        assert res[5].oid_index == "0"
        assert res[5].value == "my original location"
        assert res[5].snmp_type == "OCTETSTR"


def test_snmp_walk_unknown(sess_args):
    with pytest.raises():
        snmpwalk("systemo", **sess_args)
