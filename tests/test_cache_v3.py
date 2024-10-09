import pytest
from ezsnmp import Session


def test_v3_not_caching_user(sess_v3_md5_des):
    s = Session(**sess_v3_md5_des)
    res = s.get("sysDescr.0")

    assert res[0].oid == "sysDescr"
    assert res[0].oid_index == "0"
    assert res[0].snmp_type == "OCTETSTR"
    s.update_session(privacy_passphrase="wrong_pass")

    with pytest.raises():
        res = s.get("sysDescr.0")

    d = dict(**sess_v3_md5_des)
    d["privacy_passphrase"] = "wrong_pass"
    s = Session(**d)
    with pytest.raises():
        res = s.get("sysDescr.0")

    s.update_session(privacy_passphrase="priv_pass")
    res = s.get("sysDescr.0")

    assert res[0].oid == "sysDescr"
    assert res[0].oid_index == "0"
    assert res[0].snmp_type == "OCTETSTR"
