import pytest
from ezsnmp import Session
import faulthandler

faulthandler.enable()


def test_v3_not_caching_user(sess_v3_md5_des):
    s = Session(**sess_v3_md5_des)
    assert s.args == (
        "-A",
        "auth_pass",
        "-a",
        "MD5",
        "-c",
        "public",
        "-X",
        "priv_pass",
        "-x",
        "DES",
        "-r",
        "3",
        "-l",
        "authPriv",
        "-u",
        "initial_md5_des",
        "-t",
        "1",
        "-v",
        "3",
        "localhost:11161",
    )
    res = s.get("sysDescr.0")

    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert res[0].type == "STRING"
    s.privacy_passphrase = "wrong_pass"
    assert s.privacy_passphrase == "wrong_pass"

    with pytest.raises(RuntimeError):
        assert s.args == (
            "-A",
            "auth_pass",
            "-a",
            "MD5",
            "-c",
            "public",
            "-X",
            "wrong_pass",
            "-x",
            "DES",
            "-r",
            "3",
            "-l",
            "authPriv",
            "-u",
            "initial_md5_des",
            "-t",
            "1",
            "-v",
            "3",
            "localhost:11161",
        )
        res = s.get("sysDescr.0")

    d = dict(**sess_v3_md5_des)
    d["privacy_passphrase"] = "wrong_pass"
    s = Session(**d)
    assert s.privacy_passphrase == "wrong_pass"
    with pytest.raises(RuntimeError):
        assert s.args == (
            "-A",
            "auth_pass",
            "-a",
            "MD5",
            "-c",
            "public",
            "-X",
            "wrong_pass",
            "-x",
            "DES",
            "-r",
            "3",
            "-l",
            "authPriv",
            "-u",
            "initial_md5_des",
            "-t",
            "1",
            "-v",
            "3",
            "localhost:11161",
        )
        res = s.get("sysDescr.0")

    s.privacy_passphrase = "priv_pass"
    assert s.privacy_passphrase == "priv_pass"
    assert s.args == (
        "-A",
        "auth_pass",
        "-a",
        "MD5",
        "-c",
        "public",
        "-X",
        "priv_pass",
        "-x",
        "DES",
        "-r",
        "3",
        "-l",
        "authPriv",
        "-u",
        "initial_md5_des",
        "-t",
        "1",
        "-v",
        "3",
        "localhost:11161",
    )
    res = s.get("sysDescr.0")

    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert res[0].type == "STRING"
