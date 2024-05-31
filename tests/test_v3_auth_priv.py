from __future__ import unicode_literals

from ezsnmp.session import Session


def test_v3_authentication_md5_privacy_des(sess_v3_md5):
    s = Session(**sess_v3_md5)
    res = s.get("sysDescr.0")

    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"
    del s

def test_v3_authentication_sha_privacy_aes(sess_v3_sha):
    s = Session(**sess_v3_sha)
    res = s.get("sysDescr.0")

    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"
    del s
