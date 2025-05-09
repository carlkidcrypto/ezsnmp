from __future__ import unicode_literals

from ezsnmp.session import Session


def test_session_get_s1_then_s2(sess_v3_md5_des, sess_v3_md5_des_ipv6):
    s1 = Session(**sess_v3_md5_des)
    s2 = Session(**sess_v3_md5_des_ipv6)

    print(f"s1 = {s1.get('sysDescr.0')}")
    print(f"s2 = {s2.get('sysDescr.0')}")

    print(f"s2 = {s2.get('sysDescr.0')}")
    print(f"s1 = {s1.get('sysDescr.0')}")


def test_session_get_s2_then_s1(sess_v3_md5_des, sess_v3_md5_des_ipv6):
    s1 = Session(**sess_v3_md5_des)
    s2 = Session(**sess_v3_md5_des_ipv6)

    print(f"s2 = {s2.get('sysDescr.0')}")
    print(f"s1 = {s1.get('sysDescr.0')}")
