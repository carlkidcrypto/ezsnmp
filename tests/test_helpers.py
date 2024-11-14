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
