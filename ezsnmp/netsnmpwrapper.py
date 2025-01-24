from .netsnmp import (
    snmpbulkget as netsnmp_snmpbulkget,
    snmpget as netsnmp_snmpget,
    snmpgetnext as netsnmp_snmpgetnext,
    snmpbulkwalk as netsnmp_snmpbulkwalk,
    snmpset as netsnmp_snmpset,
    snmptrap as netsnmp_snmptrap,
    snmpwalk as netsnmp_snmpwalk
)
from .exceptions import (
    GenericError,
    ConnectionError,
    TimeoutError,
    UnknownObjectIDError,
    NoSuchNameError,
    NoSuchObjectError,
    NoSuchInstanceError,
    UndeterminedTypeError,
    ParseError,
    PacketError,
)
from sys import exit

def _handle_error(e):
    if 'GenericErrorBase' in str(type(e)):
        raise GenericError(str(e))

def snmpget(netsnmp_args):
    try:
        result = netsnmp_snmpget(netsnmp_args)
        return result
    except Exception as e :
        _handle_error(e)

def snmpgetnext(netsnmp_args):
    try:
        result = netsnmp_snmpgetnext(netsnmp_args)
        return result
    except Exception as e :
        _handle_error(e)

def snmpwalk(netsnmp_args):
    try:
        result = netsnmp_snmpwalk(netsnmp_args)
        return result
    except Exception as e :
        _handle_error(e)

def snmpbulkget(netsnmp_args):
    try:
        result = netsnmp_snmpbulkget(netsnmp_args)
        return result
    except Exception as e :
        _handle_error(e)

def snmpbulkwalk(netsnmp_args):
    try:
        result = netsnmp_snmpbulkwalk(netsnmp_args)
        return result
    except Exception as e :
        _handle_error(e)

def snmpset(netsnmp_args):
    try:
        result = netsnmp_snmpset(netsnmp_args)
        return result
    except Exception as e :
        _handle_error(e)

def snmptrap(netsnmp_args):
    try:
        netsnmp_snmptrap(netsnmp_args)
    except Exception as e :
        _handle_error(e)