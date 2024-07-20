from __future__ import unicode_literals

from ezsnmp.helpers import normalize_oid


def test_normalize_oid_just_iso():
    oid, oid_index = normalize_oid("oid")
    assert oid == "oid"
    assert oid_index == ""


def test_normalize_oid_just_period():
    oid, oid_index = normalize_oid(".")
    assert oid == "."
    assert oid_index == ""


def test_normalize_oid_regular():
    oid, oid_index = normalize_oid("sysContact.0")
    assert oid == "sysContact"
    assert oid_index == "0"


def test_normalize_oid_regular_2():
    oid, oid_index = normalize_oid("SNMPv2::mib-2.17.7.1.4.3.1.2.300")
    assert oid == "SNMPv2::mib-2"
    assert oid_index == "17.7.1.4.3.1.2.300"


def test_normalize_oid_regular_3():
    oid, oid_index = normalize_oid("nsCacheTimeout.1.3.6.1.2.1.2")
    assert oid == "nsCacheTimeout"
    assert oid_index == "1.3.6.1.2.1.2"


def test_normalize_oid_regular_4():
    oid, oid_index = normalize_oid("iso.3.6.1.2.1.31.1.1.1.1.5035")
    assert oid == "iso"
    assert oid_index == "3.6.1.2.1.31.1.1.1.1.5035"


def test_normalize_oid_numeric():
    oid, oid_index = normalize_oid(".1.3.6.1.2.1.1.1.0")
    assert oid == ".1.3.6.1.2.1.1.1.0"
    assert oid_index == ""


def test_normalize_oid_full_qualified():
    oid, oid_index = normalize_oid(".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0")
    assert oid == ".iso.org.dod.internet.mgmt.mib-2.system.sysDescr"
    assert oid_index == "0"


def test_normalize_oid_with_index():
    oid, oid_index = normalize_oid("abc", "def")
    assert oid == "abc"
    assert oid_index == "def"
