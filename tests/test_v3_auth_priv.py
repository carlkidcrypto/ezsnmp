from __future__ import unicode_literals

from ezsnmp.session import Session


def test_v3_authentication_md5_privacy_des(sess_v3_md5_des):
    s = Session(**sess_v3_md5_des)

    assert s.auth_password == "auth_pass"
    assert s.auth_protocol == "MD5"
    assert s.privacy_password == "priv_pass"
    assert s.privacy_protocol == "DES"

    res = s.get("sysDescr.0")

    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"
    del s


def test_v3_authentication_md5_privacy_aes(sess_v3_md5_aes):
    s = Session(**sess_v3_md5_aes)

    assert s.auth_password == "auth_pass"
    assert s.auth_protocol == "MD5"
    assert s.privacy_password == "priv_pass"
    assert s.privacy_protocol == "AES"

    res = s.get("sysDescr.0")

    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"
    del s


def test_v3_authentication_sha_privacy_aes(sess_v3_sha_aes):
    s = Session(**sess_v3_sha_aes)

    assert s.auth_password == "auth_second"
    assert s.auth_protocol == "SHA"
    assert s.privacy_password == "priv_second"
    assert s.privacy_protocol == "AES"

    res = s.get("sysDescr.0")

    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"
    del s


def test_v3_authentication_sha_no_priv(sess_v3_sha_no_priv):
    s = Session(**sess_v3_sha_no_priv)

    assert s.auth_password == "auth_second"
    assert s.auth_protocol == "SHA"
    assert s.privacy_password == ""
    assert s.privacy_protocol == "DEFAULT"

    res = s.get("sysDescr.0")

    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"
    del s


def test_v3_authentication_md5_no_priv(sess_v3_md5_no_priv):
    s = Session(**sess_v3_md5_no_priv)

    assert s.auth_password == "auth_pass"
    assert s.auth_protocol == "MD5"
    assert s.privacy_password == ""
    assert s.privacy_protocol == "DEFAULT"

    res = s.get("sysDescr.0")

    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"
    del s
