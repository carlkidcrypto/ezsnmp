from __future__ import unicode_literals

from ezsnmp.session import Session
import pytest

@pytest.fixture
def get_netsnmp_sess_args():
    def _get_args(ip, version, auth_type=None):
        if version == "v1" or version == "v2c":
            for args in NETSNMP_SESS_ARGS[version]:
                if ip in args[-1]:
                    return args
        elif version == "v3" and auth_type:
            for args in NETSNMP_SESS_ARGS["v3"][auth_type]:
                if ip in args[-1]:
                    return args
        raise ValueError(f"No matching session arguments found for IP: {ip}, version: {version}, auth_type: {auth_type}")
    return _get_args

NETSNMP_SESS_ARGS = {
    "v1": [
        ["-v", "1", "-c", "public", "192.168.1.3:11161"],
        ["-v", "1", "-c", "public", "192.168.1.4:11161"],
    ],
    "v2c": [
        ["-v", "2c", "-c", "public", "192.168.1.3:11161"],
        ["-v", "2c", "-c", "public", "192.168.1.4:11161"],
    ],
    "v3": {
        "md5_des": [
            [
                "-v", "3", "-a", "MD5", "-l", "authPriv", "-u", "initial_md5_des",
                "-x", "DES", "-X", "priv_pass", "-A", "auth_pass", "192.168.1.3:11161"
            ],
            [
                "-v", "3", "-a", "MD5", "-l", "authPriv", "-u", "initial_md5_des",
                "-x", "DES", "-X", "priv_pass", "-A", "auth_pass", "192.168.1.4:11161"
            ],
        ],
        "md5_aes": [
            [
                "-v", "3", "-a", "MD5", "-l", "authPriv", "-u", "initial_md5_aes",
                "-x", "AES", "-X", "priv_pass", "-A", "auth_pass", "192.168.1.3:11161"
            ],
            [
                "-v", "3", "-a", "MD5", "-l", "authPriv", "-u", "initial_md5_aes",
                "-x", "AES", "-X", "priv_pass", "-A", "auth_pass", "192.168.1.4:11161"
            ],
        ],
        "sha_aes": [
            [
                "-v", "3", "-a", "SHA", "-l", "authPriv", "-u", "secondary_sha_aes",
                "-x", "AES", "-X", "priv_second", "-A", "auth_second", "192.168.1.3:11161"
            ],
            [
                "-v", "3", "-a", "SHA", "-l", "authPriv", "-u", "secondary_sha_aes",
                "-x", "AES", "-X", "priv_second", "-A", "auth_second", "192.168.1.4:11161"
            ],
        ],
        "sha_no_priv": [
            [
                "-v", "3", "-a", "SHA", "-l", "authNoPriv", "-u", "secondary_sha_no_priv",
                "-A", "auth_second", "192.168.1.3:11161"
            ],
            [
                "-v", "3", "-a", "SHA", "-l", "authNoPriv", "-u", "secondary_sha_no_priv",
                "-A", "auth_second", "192.168.1.4:11161"
            ],
        ],
        "md5_no_priv": [
            [
                "-v", "3", "-a", "MD5", "-l", "authNoPriv", "-u", "initial_md5_no_priv",
                "-A", "auth_pass", "192.168.1.3:11161"
            ],
            [
                "-v", "3", "-a", "MD5", "-l", "authNoPriv", "-u", "initial_md5_no_priv",
                "-A", "auth_pass", "192.168.1.4:11161"
            ],
        ],
    },
}

def test_session_get_s1_then_s2(get_netsnmp_sess_args):
    sess_v3_md5_des_s1 = get_netsnmp_sess_args("192.168.1.3:11161", "v3", "md5_des")
    sess_v3_md5_des_s2 = get_netsnmp_sess_args("192.168.1.4:11161", "v3", "md5_des")

    s1 = Session(*sess_v3_md5_des_s1)
    s2 = Session(*sess_v3_md5_des_s2)

    print(f"s1 = {s1.get('sysDescr.0')}")
    print(f"s2 = {s2.get('sysDescr.0')}")

    print(f"s2 = {s2.get('sysDescr.0')}")
    print(f"s1 = {s1.get('sysDescr.0')}")


def test_session_get_s2_then_s1(get_netsnmp_sess_args):
    sess_v3_md5_des_s1 = get_netsnmp_sess_args("192.168.1.3:11161", "v3", "md5_des")
    sess_v3_md5_des_s2 = get_netsnmp_sess_args("192.168.1.4:11161", "v3", "md5_des")

    s1 = Session(*sess_v3_md5_des_s1)
    s2 = Session(*sess_v3_md5_des_s2)

    print(f"s2 = {s2.get('sysDescr.0')}")
    print(f"s1 = {s1.get('sysDescr.0')}")

    print(f"s1 = {s1.get('sysDescr.0')}")
    print(f"s2 = {s2.get('sysDescr.0')}")
