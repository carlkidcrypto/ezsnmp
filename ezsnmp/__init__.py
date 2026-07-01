"""
EzSnmp — a Python/C++ SNMP library wrapping Net-SNMP.

Provides a high-level :class:`~ezsnmp.session.Session` class for SNMP v1,
v2c, and v3 operations (GET, GETNEXT, WALK, BULKGET, BULKWALK, SET), as well
as low-level functional wrappers (:func:`snmpget`, :func:`snmpwalk`, etc.)
that accept raw Net-SNMP command-line argument lists.

Typical usage::

    from ezsnmp import Session

    with Session(hostname='localhost', community='public', version=2) as session:
        results = session.get(['sysDescr.0', 'sysLocation.0'])
        for item in results:
            print(item.oid, item.value)
"""
from .datatypes import Result
from .exceptions import (
    ConnectionError,
    GenericError,
    NoSuchInstanceError,
    NoSuchNameError,
    NoSuchObjectError,
    PacketError,
    ParseError,
    TimeoutError,
    UndeterminedTypeError,
    UnknownObjectIDError,
    _handle_error,
)
from .netsnmp import (
    snmpbulkget,
    snmpbulkwalk,
    snmpget,
    snmpgetnext,
    snmpset,
    snmptrap,
    snmpwalk,
)
from .session import Session
