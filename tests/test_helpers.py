import pytest
from ezsnmp import Session
import faulthandler

faulthandler.enable()


def test_normalize_oid_just_iso(sess):
    res = sess.get("oid")
    assert res[0].oid == "oid"
    assert res[0].index == ""


def test_normalize_oid_just_period(sess):
    res = sess.get(".")
    assert res[0].oid == "."
    assert res[0].index == ""


def test_normalize_oid_regular(sess):
    res = sess.get("sysContact.0")
    assert res[0].oid == "sysContact"
    assert res[0].index == "0"


def test_normalize_oid_regular_2(sess):
    res = sess.get("SNMPv2::mib-2.17.7.1.4.3.1.2.300")
    assert res[0].oid == "SNMPv2::mib-2"
    assert res[0].index == "17.7.1.4.3.1.2.300"


def test_normalize_oid_regular_3(sess):
    res = sess.get("nsCacheTimeout.1.3.6.1.2.1.2")
    assert res[0].oid == "nsCacheTimeout"
    assert res[0].index == "1.3.6.1.2.1.2"


def test_normalize_oid_regular_4(sess):
    res = sess.get("iso.3.6.1.2.1.31.1.1.1.1.5035")
    assert res[0].oid == "iso"
    assert res[0].index == "3.6.1.2.1.31.1.1.1.1.5035"


def test_normalize_oid_numeric(sess):
    res = sess.get(".1.3.6.1.2.1.1.1.0")
    assert res[0].oid == ".1.3.6.1.2.1.1.1.0"
    assert res[0].index == ""


def test_normalize_oid_full_qualified(sess):
    res = sess.get(".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0")
    assert res[0].oid == ".iso.org.dod.internet.mgmt.mib-2.system.sysDescr"
    assert res[0].index == "0"


def test_normalize_oid_with_index(sess):
    res = sess.get("abc", "def")
    assert res[0].oid == "abc"
    assert res[0].index == "def"
