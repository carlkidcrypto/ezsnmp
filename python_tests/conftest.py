import pytest
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
    """An exception raised when an SNMP SET fails via the CLI."""

    pass


def snmp_set_via_cli(oid, value, type):
    """
    Sets an SNMP variable using the snmpset command.

    :param oid: the OID to update
    :param value: the new value to set the OID to
    :param type: a single character type as required by the snmpset command
                    (i: INTEGER, u: unsigned INTEGER, t: TIMETICKS,
                    a: IPADDRESS o: OBJID, s: STRING, x: HEX STRING,
                    d: DECIMAL STRING, b: BITS U: unsigned int64,
                    I: signed int64, F: float, D: double)
    """
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


def _get_netsnmp_params():
    params = [
        NETSNMP_SESS_V1_ARGS,
        NETSNMP_SESS_V2_ARGS,
        NETSNMP_SESS_V3_MD5_AES_ARGS,
        NETSNMP_SESS_V3_SHA_AES_ARGS,
    ]
    if is_des_supported():
        params.insert(2, NETSNMP_SESS_V3_MD5_DES_ARGS)
    return params


@pytest.fixture(params=_get_netsnmp_params())
def netsnmp_args(request):
    return request.param


@pytest.fixture
def netsnmp(netsnmp_args):
    return netsnmp_args


def _get_sess_params():
    params = [
        SESS_V1_ARGS,
        SESS_V2_ARGS,
        SESS_V3_MD5_AES_ARGS,
        SESS_V3_SHA_AES_ARGS,
    ]
    if is_des_supported():
        params.insert(2, SESS_V3_MD5_DES_ARGS)
    return params


@pytest.fixture(params=_get_sess_params())
def sess_args(request):
    return request.param


@pytest.fixture
def sess(sess_args):
    return ezsnmp.Session(**sess_args)


@pytest.fixture
def reset_values():
    yield None
    snmp_set_via_cli("sysLocation.0", "my original location", "s")
    snmp_set_via_cli("nsCacheTimeout.1.3.6.1.2.1.2.2", "0", "i")


@pytest.fixture
def sess_v3_md5_des():
    return SESS_V3_MD5_DES_ARGS


@pytest.fixture
def sess_v2():
    return SESS_V2_ARGS


@pytest.fixture
def sess_v3_md5_aes():
    return SESS_V3_MD5_AES_ARGS


@pytest.fixture
def sess_v3_sha_aes():
    return SESS_V3_SHA_AES_ARGS


@pytest.fixture
def sess_v3_sha_no_priv():
    return SESS_V3_SHA_NO_PRIV_ARGS


@pytest.fixture
def sess_v3_md5_no_priv():
    return SESS_V3_MD5_NO_PRIV_ARGS


@pytest.fixture
def netsnmp_v3_md5_des():
    return NETSNMP_SESS_V3_MD5_DES_ARGS


@pytest.fixture
def netsnmp_v3_md5_aes():
    return NETSNMP_SESS_V3_MD5_AES_ARGS


@pytest.fixture
def netsnmp_v3_sha_aes():
    return NETSNMP_SESS_V3_SHA_AES_ARGS


@pytest.fixture
def netsnmp_v3_sha_no_priv():
    return NETSNMP_SESS_V3_SHA_NO_PRIV_ARGS


@pytest.fixture
def netsnmp_v3_md5_no_priv():
    return NETSNMP_SESS_V3_MD5_NO_PRIV_ARGS
