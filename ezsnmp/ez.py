from __future__ import unicode_literals, absolute_import

from typing import Union, List, Tuple, Any, overload, Optional

from .session import Session
from .variables import SNMPVariable


@overload
def snmp_get(
    oids: List[Union[str, Tuple[str, str]]], **session_kargs: dict
) -> List[SNMPVariable]: ...


@overload
def snmp_get(
    oids: Union[str, Tuple[str, str]], **session_kargs: dict
) -> SNMPVariable: ...


def snmp_get(
    oids: Union[List[Union[str, Tuple[str, str]]], Union[str, Tuple[str, str]]],
    **session_kargs: dict,
) -> Union[SNMPVariable, List[SNMPVariable]]:
    """
    Perform an SNMP GET operation to retrieve a particular piece of
    information.

    :param oids: you may pass in a list of OIDs or single item; each item
                 may be a string representing the entire OID
                 (e.g. 'sysDescr.0') or may be a tuple containing the
                 name as its first item and index as its second
                 (e.g. ('sysDescr', 0))
    :param session_kargs: keyword arguments which will be sent used when
                          constructing the session for this operation;
                          all parameters in the Session class are supported
    :return: an SNMPVariable object containing the value that was
                 retrieved or a list of objects when you send in a list of
                 OIDs
    """

    session = Session(**session_kargs)
    retval = session.get(oids)
    del session
    return retval


def snmp_set(
    oid: Union[str, Tuple[str, str]],
    value: Any,
    type: Optional[str] = None,
    **session_kargs: dict,
) -> bool:
    """
    Perform an SNMP SET operation to update a particular piece of
    information.

    :param oid: the OID that you wish to set which may be a string
                representing the entire OID (e.g. 'sysDescr.0') or may
                be a tuple containing the name as its first item and
                index as its second (e.g. ('sysDescr', 0))
    :param value: the value to set the OID to
    :param snmp_type: if a numeric OID is used and the object is not in
                      the parsed MIB, a type must be explicitly supplied
    :param session_kargs: keyword arguments which will be sent used when
                          constructing the session for this operation;
                          all parameters in the Session class are supported
    :return: bool value indicated that if snmp_set was successed
    """

    session = Session(**session_kargs)
    retval = session.set(oid, value, type)
    del session
    return retval


def snmp_set_multiple(
    oid_values: List[Union[Tuple[str, Any], Tuple[str, Any, str]]], **session_kargs: dict
) -> bool:
    """
    Perform multiple SNMP SET operations to update various pieces of
    information at the same time.

    :param oid_values: a list of tuples whereby each tuple contains a
                       (oid, value) or an (oid, value, snmp_type)
    :param session_kargs: keyword arguments which will be sent used when
                          constructing the session for this operation;
                          all parameters in the Session class are supported
    :return: bool value indicated that if snmp_set was successed
    """

    session = Session(**session_kargs)
    retval = session.set_multiple(oid_values)
    del session
    return retval


@overload
def snmp_get_next(
    oids: List[Union[str, Tuple[str, str]]], **session_kargs: dict
) -> List[SNMPVariable]: ...


@overload
def snmp_get_next(
    oids: Union[str, Tuple[str, str]], **session_kwargs: Any
) -> SNMPVariable: ...


def snmp_get_next(
    oids: Union[List[Union[str, Tuple[str, str]]], Union[str, Tuple[str, str]]],
    **session_kargs: dict,
) -> Union[List[SNMPVariable], SNMPVariable]:
    """
    Uses an SNMP GETNEXT operation to retrieve the next variable after
    the chosen item.

    :param oids: you may pass in a list of OIDs or single item; each item
                 may be a string representing the entire OID
                 (e.g. 'sysDescr.0') or may be a tuple containing the
                 name as its first item and index as its second
                 (e.g. ('sysDescr', 0))
    :param session_kargs: keyword arguments which will be sent used when
                          constructing the session for this operation;
                          all parameters in the Session class are supported
    :return: an SNMPVariable object containing the value that was
                 retrieved or a list of objects when you send in a list of
                 OIDs
    """

    session = Session(**session_kargs)
    retval = session.get_next(oids)
    del session
    return retval


def snmp_get_bulk(
    oids: Union[List[Union[str, Tuple[str, str]]], Union[str, Tuple[str, str]]],
    non_repeaters: int = 0,
    max_repetitions: int = 10,
    **session_kargs: dict,
) -> List[SNMPVariable]:
    """
    Performs a bulk SNMP GET operation to retrieve multiple pieces of
    information in a single packet.

    :param oids: you may pass in a list of OIDs or single item; each item
                 may be a string representing the entire OID
                 (e.g. 'sysDescr.0') or may be a tuple containing the
                 name as its first item and index as its second
                 (e.g. ('sysDescr', 0))
    :param non_repeaters: the number of objects that are only expected to
                          return a single GETNEXT instance, not multiple
                          instances
    :param max_repetitions: the number of objects that should be returned
                            for all the repeating OIDs
    :param session_kargs: keyword arguments which will be sent used when
                          constructing the session for this operation;
                          all parameters in the Session class are supported
    :return: a list of SNMPVariable objects containing the values that
             were retrieved via SNMP
    """

    session = Session(**session_kargs)
    retval = session.get_bulk(oids, non_repeaters, max_repetitions)
    del session
    return retval


def snmp_walk(
    oids: Union[
        List[Union[str, Tuple[str, str]]], Union[str, Tuple[str, str]]
    ] = ".1.3.6.1.2.1",
    **session_kargs: dict,
) -> List[SNMPVariable]:
    """
    Uses SNMP GETNEXT operation to automatically retrieve multiple
    pieces of information in an OID for you.

    :param oids: you may pass in a single item (multiple values currently
                 experimental) which may be a string representing the
                 entire OID (e.g. 'sysDescr.0') or may be a tuple
                 containing the name as its first item and index as its
                 second (e.g. ('sysDescr', 0))
    :param session_kargs: keyword arguments which will be sent used when
                          constructing the session for this operation;
                          all parameters in the Session class are supported
    :return: a list of SNMPVariable objects containing the values that
             were retrieved via SNMP
    """

    session = Session(**session_kargs)
    retval = session.walk(oids)
    del session
    return retval


def snmp_bulkwalk(
    oids: Union[
        List[Union[str, Tuple[str, str]]], Union[str, Tuple[str, str]]
    ] = ".1.3.6.1.2.1",
    non_repeaters: int = 0,
    max_repetitions: int = 10,
    **session_kargs: dict,
) -> List[SNMPVariable]:
    """
    Uses SNMP GETBULK operation using the prepared session to
    automatically retrieve multiple pieces of information in an OID

    :param oids: you may pass in a single item
                 * string representing the
                 entire OID (e.g. 'sysDescr.0')
                 * tuple (name, index) (e.g. ('sysDescr', 0))
                 * list of OIDs
    :param non_repeaters: the number of objects that are only expected to
                          return a single GETNEXT instance, not multiple
                          instances
    :param max_repetitions: the number of objects that should be returned
                            for all the repeating OIDs
    :return: a list of SNMPVariable objects containing the values that
             were retrieved via SNMP
    """

    session = Session(**session_kargs)
    retval = session.bulkwalk(oids, non_repeaters, max_repetitions)
    del session
    return retval
