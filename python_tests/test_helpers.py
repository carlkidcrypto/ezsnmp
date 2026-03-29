import faulthandler

faulthandler.enable()


def test_normalize_oid_regular(sess):
    res = sess.get("sysContact.0")
    assert res[0].oid == "SNMPv2-MIB::sysContact"
    assert res[0].index == "0"


def test_normalize_oid_numeric(sess):
    res = sess.get(".1.3.6.1.2.1.1.1.0")
    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"


def test_normalize_oid_full_qualified(sess):
    res = sess.get(".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0")
    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"


def test_multiline_string_value(sess, reset_values):
    """Test that multi-line string values are fully returned, not truncated at the first newline.

    Regression test for the bug where parse_result used std::getline without a delimiter,
    causing only the first line of a multi-line SNMP string response to be captured.
    """
    multiline_value = "ezsnmp line one\nezsnmp line two\nezsnmp line three"

    success = sess.set(["sysLocation.0", "s", multiline_value])
    assert success

    res = sess.get("sysLocation.0")
    assert res[0].value == multiline_value
