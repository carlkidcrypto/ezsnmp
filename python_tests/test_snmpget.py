import platform

import faulthandler
import pytest

from ezsnmp.exceptions import GenericError, PacketError
from ezsnmp.netsnmp import snmpget

faulthandler.enable()


def test_regular(netsnmp_args):
    netsnmp_args = netsnmp_args + ["sysDescr.0"]
    res = snmpget(netsnmp_args, "testing_value")

    assert platform.version() in res[0].value
    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert res[0].type == "STRING"


def test_fully_qualified(netsnmp_args):
    netsnmp_args = netsnmp_args + [".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0"]
    res = snmpget(netsnmp_args, "testing_value")

    assert platform.version() in res[0].value
    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert res[0].type == "STRING"


def test_numeric(netsnmp_args):
    netsnmp_args = netsnmp_args + [".1.3.6.1.2.1.1.1.0"]
    res = snmpget(netsnmp_args, "testing_value")

    assert platform.version() in res[0].value
    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert res[0].type == "STRING"


def test_numeric_no_leading_dot(netsnmp_args):
    netsnmp_args = netsnmp_args + ["1.3.6.1.2.1.1.1.0"]
    res = snmpget(netsnmp_args, "testing_value")

    assert platform.version() in res[0].value
    assert res[0].oid == "SNMPv2-MIB::sysDescr"
    assert res[0].index == "0"
    assert res[0].type == "STRING"


def test_unknown(netsnmp_args):
    with pytest.raises(GenericError):
        netsnmp_args = netsnmp_args + ["sysDescripto.0"]
        snmpget(netsnmp_args, "testing_value")


def test_invalid_instance(netsnmp_args):
    # Sadly, SNMP v1 doesn't distinguish between an invalid instance and an
    # invalid object ID, instead it excepts with noSuchName
    if netsnmp_args[1] == "1":
        if platform.system() != "Darwin":
            with pytest.raises(PacketError):
                netsnmp_args = netsnmp_args + ["sysContact.1"]
                # On Mac `snmpwalk -v 1 -c public localhost:11161 sysContact.1`
                # produces no output, but on Ubuntu it does...
                snmpget(netsnmp_args, "testing_value")
    else:
        netsnmp_args = netsnmp_args + ["sysContact.1"]
        res = snmpget(netsnmp_args, "testing_value")
        assert res[0].type in ["NOSUCHINSTANCE", "NOSUCHOBJECT"]


def test_invalid_object(netsnmp_args):
    if netsnmp_args[1] == "1":
        with pytest.raises(PacketError):
            netsnmp_args = netsnmp_args + ["iso"]
            snmpget(netsnmp_args, "testing_value")
    else:
        netsnmp_args = netsnmp_args + ["iso"]
        res = snmpget(netsnmp_args, "testing_value")
        assert res[0].type == "NOSUCHOBJECT"
