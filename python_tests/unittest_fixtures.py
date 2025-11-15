import unittest
from subprocess import Popen, DEVNULL
import ezsnmp
import platform
from session_parameters import (
    SESS_V1_ARGS,
    SESS_V2_ARGS,
    SESS_V3_MD5_DES_ARGS,
    SESS_V3_MD5_AES_ARGS,
    SESS_V3_SHA_AES_ARGS,
    SESS_V3_SHA_NO_PRIV_ARGS,
    SESS_V3_MD5_NO_PRIV_ARGS,
)

from netsnmp_parameters import (
    NETSNMP_SESS_V1_ARGS,
    NETSNMP_SESS_V2_ARGS,
    NETSNMP_SESS_V3_MD5_DES_ARGS,
    NETSNMP_SESS_V3_MD5_AES_ARGS,
    NETSNMP_SESS_V3_SHA_AES_ARGS,
    NETSNMP_SESS_V3_SHA_NO_PRIV_ARGS,
    NETSNMP_SESS_V3_MD5_NO_PRIV_ARGS,
)

from platform_compat import is_des_supported


class SNMPSetCLIError(Exception):
    pass


def snmp_set_via_cli(oid, value, type):
    process = Popen(
        "snmpset -v2c -c public localhost:11161 {} {} {}".format(
            oid, type, '"{}"'.format(value) if type == "s" else value
        ),
        stdout=DEVNULL,
        stderr=DEVNULL,
        shell=True,
    )
    process.communicate()
    if process.returncode != 0:
        raise SNMPSetCLIError(
            "failed to set {0} to {1} (type {2})".format(oid, value, type)
        )


def get_netsnmp_params():
    params = [
        NETSNMP_SESS_V1_ARGS,
        NETSNMP_SESS_V2_ARGS,
        NETSNMP_SESS_V3_MD5_AES_ARGS,
        NETSNMP_SESS_V3_SHA_AES_ARGS,
    ]
    if is_des_supported():
        params.insert(2, NETSNMP_SESS_V3_MD5_DES_ARGS)
    return params


def get_sess_params():
    params = [
        SESS_V1_ARGS,
        SESS_V2_ARGS,
        SESS_V3_MD5_AES_ARGS,
        SESS_V3_SHA_AES_ARGS,
    ]
    if is_des_supported():
        params.insert(2, SESS_V3_MD5_DES_ARGS)
    return params


class BaseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sess_params = get_sess_params()
        cls.netsnmp_params = get_netsnmp_params()
        cls.sess_v3_md5_des = SESS_V3_MD5_DES_ARGS
        cls.sess_v3_md5_aes = SESS_V3_MD5_AES_ARGS
        cls.sess_v3_sha_aes = SESS_V3_SHA_AES_ARGS
        cls.sess_v3_sha_no_priv = SESS_V3_SHA_NO_PRIV_ARGS
        cls.sess_v3_md5_no_priv = SESS_V3_MD5_NO_PRIV_ARGS
        cls.netsnmp_v3_md5_des = NETSNMP_SESS_V3_MD5_DES_ARGS
        cls.netsnmp_v3_md5_aes = NETSNMP_SESS_V3_MD5_AES_ARGS
        cls.netsnmp_v3_sha_aes = NETSNMP_SESS_V3_SHA_AES_ARGS
        cls.netsnmp_v3_sha_no_priv = NETSNMP_SESS_V3_SHA_NO_PRIV_ARGS
        cls.netsnmp_v3_md5_no_priv = NETSNMP_SESS_V3_MD5_NO_PRIV_ARGS

    def reset_snmp_values(self):
        snmp_set_via_cli("sysLocation.0", "my original location", "s")
        snmp_set_via_cli("nsCacheTimeout.1.3.6.1.2.1.2.2", "0", "i")
