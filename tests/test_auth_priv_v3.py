from ezsnmp import Session
from time import sleep
from random import uniform


def test_v3_authentication_md5_privacy_des(sess_v3_md5_des):
    s = Session(**sess_v3_md5_des)

    assert s.auth_passphrase == "auth_pass"
    assert s.auth_protocol == "MD5"
    assert s.privacy_passphrase == "priv_pass"
    assert s.privacy_protocol == "DES"

    res = s.get("sysDescr.0")

    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert res[0].type == "STRING"
    del s


def test_v3_authentication_md5_privacy_aes(sess_v3_md5_aes):
    # Space out our tests to avoid overwhelming the snmpd server with traffic.
    sleep(uniform(0.1, 0.25))
    s = Session(**sess_v3_md5_aes)

    assert s.auth_passphrase == "auth_pass"
    assert s.auth_protocol == "MD5"
    assert s.privacy_passphrase == "priv_pass"
    assert s.privacy_protocol == "AES"

    res = s.get("sysDescr.0")

    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert res[0].type == "STRING"
    del s


def test_v3_authentication_sha_privacy_aes(sess_v3_sha_aes):
    # Space out our tests to avoid overwhelming the snmpd server with traffic.
    sleep(uniform(0.1, 0.25))
    s = Session(**sess_v3_sha_aes)

    assert s.auth_passphrase == "auth_second"
    assert s.auth_protocol == "SHA"
    assert s.privacy_passphrase == "priv_second"
    assert s.privacy_protocol == "AES"

    res = s.get("sysDescr.0")

    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert res[0].type == "STRING"
    del s


def test_v3_authentication_sha_no_priv(sess_v3_sha_no_priv):
    # Space out our tests to avoid overwhelming the snmpd server with traffic.
    sleep(uniform(0.1, 0.25))
    s = Session(**sess_v3_sha_no_priv)

    assert s.auth_passphrase == "auth_second"
    assert s.auth_protocol == "SHA"
    assert s.privacy_passphrase == ""
    assert s.privacy_protocol == ""

    res = s.get("sysDescr.0")

    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert res[0].type == "STRING"
    del s


def test_v3_authentication_md5_no_priv(sess_v3_md5_no_priv):
    # Space out our tests to avoid overwhelming the snmpd server with traffic.
    sleep(uniform(0.1, 0.25))
    s = Session(**sess_v3_md5_no_priv)

    assert s.auth_passphrase == "auth_pass"
    assert s.auth_protocol == "MD5"
    assert s.privacy_passphrase == ""
    assert s.privacy_protocol == ""

    res = s.get("sysDescr.0")

    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert res[0].type == "STRING"
    del s
