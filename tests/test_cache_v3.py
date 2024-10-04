import pytest
from ezsnmp import Session


def test_v3_not_caching_user(sess_v3_md5_des):
    s = Session(**sess_v3_md5_des)
    res = s.get("sysDescr.0")

    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"
    s.update_session(privacy_password="wrong_pass")

    with pytest.raises():
        res = s.get("sysDescr.0")

    d = dict(**sess_v3_md5_des)
    d["privacy_password"] = "wrong_pass"
    s = Session(**d)
    with pytest.raises():
        res = s.get("sysDescr.0")

    s.update_session(privacy_password="priv_pass")
    res = s.get("sysDescr.0")

    assert res.oid == "sysDescr"
    assert res.oid_index == "0"
    assert res.snmp_type == "OCTETSTR"
