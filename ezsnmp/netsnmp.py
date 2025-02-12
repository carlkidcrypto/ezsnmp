from .netsnmpbase import (
    snmpbulkget as netsnmp_snmpbulkget,
    snmpbulkwalk as netsnmp_snmpbulkwalk,
    snmpget as netsnmp_snmpget,
    snmpgetnext as netsnmp_snmpgetnext,
    snmpset as netsnmp_snmpset,
    snmptrap as netsnmp_snmptrap,
    snmpwalk as netsnmp_snmpwalk,
)
from .exceptions import _handle_error


def snmpget(netsnmp_args=[]):
    """
    Perform an SNMP GET operation using the provided arguments.

    This function uses the `netsnmp_snmpget` function to perform an SNMP GET
    operation and returns the result.

    :param netsnmp_args: The arguments required for the SNMP GET operation
    :type netsnmp_args: list
    :return: A tuple of Result objects containing SNMP variable bindings. Each Result object has
            attributes: oid (str), index (str), value (str), and type (str)
    :rtype: tuple[Result]

    :raises ConnectionError: If the exception type is `ConnectionErrorBase`
    :raises GenericError: If the exception type is `GenericErrorBase`
    :raises NoSuchInstanceError: If the exception type is `NoSuchInstanceErrorBase`
    :raises NoSuchNameError: If the exception type is `NoSuchNameErrorBase`
    :raises NoSuchObjectError: If the exception type is `NoSuchObjectErrorBase`
    :raises PacketError: If the exception type is `PacketErrorBase`
    :raises ParseError: If the exception type is `ParseErrorBase`
    :raises TimeoutError: If the exception type is `TimeoutErrorBase`
    :raises UndeterminedTypeError: If the exception type is `UndeterminedTypeErrorBase`
    :raises UnknownObjectIDError: If the exception type is `UnknownObjectIDErrorBase`
    :raises Exception: If the exception type does not match any of the above

    Example:
        >>> from ezsnmp.netsnmp import snmpget
        >>> NETSNMP_SESS_V2_ARGS = ["-v", "2c", "-c", "public", "localhost:11161"]
        >>> netsnmp_args = NETSNMP_SESS_V2_ARGS + [".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0"]
        >>> result = snmpget(netsnmp_args)
        >>> print("OID:", result.oid)
        >>> print("Index:", result.index)
        >>> print("Value:", result.value)
        >>> print("Type:", result.type)
    """
    try:
        result = netsnmp_snmpget(netsnmp_args)
        return result
    except Exception as e:
        _handle_error(e)


def snmpgetnext(netsnmp_args=[]):
    """
    Perform an SNMP GETNEXT operation using the provided arguments.

    This function uses the `netsnmp_snmpgetnext` function to perform an SNMP GETNEXT
    operation and returns the result.

    :param netsnmp_args: The arguments required for the SNMP GETNEXT operation
    :type netsnmp_args: list
    :return: A tuple of Result objects containing SNMP variable bindings. Each Result object has
            attributes: oid (str), index (str), value (str), and type (str)
    :rtype: tuple[Result]

    :raises ConnectionError: If the exception type is `ConnectionErrorBase`
    :raises GenericError: If the exception type is `GenericErrorBase`
    :raises NoSuchInstanceError: If the exception type is `NoSuchInstanceErrorBase`
    :raises NoSuchNameError: If the exception type is `NoSuchNameErrorBase`
    :raises NoSuchObjectError: If the exception type is `NoSuchObjectErrorBase`
    :raises PacketError: If the exception type is `PacketErrorBase`
    :raises ParseError: If the exception type is `ParseErrorBase`
    :raises TimeoutError: If the exception type is `TimeoutErrorBase`
    :raises UndeterminedTypeError: If the exception type is `UndeterminedTypeErrorBase`
    :raises UnknownObjectIDError: If the exception type is `UnknownObjectIDErrorBase`
    :raises Exception: If the exception type does not match any of the above

    Example:
        >>> from ezsnmp.netsnmp import snmpgetnext
        >>> NETSNMP_SESS_V2_ARGS = ["-v", "2c", "-c", "public", "localhost:11161"]
        >>> netsnmp_args = NETSNMP_SESS_V2_ARGS + [".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0"]
        >>> result = snmpgetnext(netsnmp_args)
        >>> print("OID:", result.oid)
        >>> print("Index:", result.index)
        >>> print("Value:", result.value)
        >>> print("Type:", result.type)
    """
    try:
        result = netsnmp_snmpgetnext(netsnmp_args)
        return result
    except Exception as e:
        _handle_error(e)


def snmpwalk(netsnmp_args=[]):
    """
    Perform an SNMP WALK operation using the provided arguments.

    This function uses the `netsnmp_snmpwalk` function to perform an SNMP WALK
    operation and returns the result.

    :param netsnmp_args: The arguments required for the SNMP WALK operation
    :type netsnmp_args: list
    :return: A tuple of Result objects containing SNMP variable bindings. Each Result object has
            attributes: oid (str), index (str), value (str), and type (str)
    :rtype: tuple[Result]

    :raises ConnectionError: If the exception type is `ConnectionErrorBase`
    :raises GenericError: If the exception type is `GenericErrorBase`
    :raises NoSuchInstanceError: If the exception type is `NoSuchInstanceErrorBase`
    :raises NoSuchNameError: If the exception type is `NoSuchNameErrorBase`
    :raises NoSuchObjectError: If the exception type is `NoSuchObjectErrorBase`
    :raises PacketError: If the exception type is `PacketErrorBase`
    :raises ParseError: If the exception type is `ParseErrorBase`
    :raises TimeoutError: If the exception type is `TimeoutErrorBase`
    :raises UndeterminedTypeError: If the exception type is `UndeterminedTypeErrorBase`
    :raises UnknownObjectIDError: If the exception type is `UnknownObjectIDErrorBase`
    :raises Exception: If the exception type does not match any of the above

    Example:
        >>> from ezsnmp.netsnmp import snmpwalk
        >>> NETSNMP_SESS_V2_ARGS = ["-v", "2c", "-c", "public", "localhost:11161"]
        >>> netsnmp_args = NETSNMP_SESS_V2_ARGS + [".iso.org.dod.internet.mgmt.mib-2.system.sysDescr"]
        >>> result = snmpwalk(netsnmp_args)
        >>> print("OID:", result.oid)
        >>> print("Index:", result.index)
        >>> print("Value:", result.value)
        >>> print("Type:", result.type)
    """
    try:
        result = netsnmp_snmpwalk(netsnmp_args)
        return result
    except Exception as e:
        _handle_error(e)


def snmpbulkget(netsnmp_args=[]):
    """
    Perform an SNMP BULKGET operation using the provided arguments.

    This function uses the `netsnmp_snmpbulkget` function to perform an SNMP BULKGET
    operation and returns the result.

    :param netsnmp_args: The arguments required for the SNMP BULKGET operation
    :type netsnmp_args: list
    :return: A tuple of Result objects containing SNMP variable bindings. Each Result object has
            attributes: oid (str), index (str), value (str), and type (str)
    :rtype: tuple[Result]

    :raises ConnectionError: If the exception type is `ConnectionErrorBase`
    :raises GenericError: If the exception type is `GenericErrorBase`
    :raises NoSuchInstanceError: If the exception type is `NoSuchInstanceErrorBase`
    :raises NoSuchNameError: If the exception type is `NoSuchNameErrorBase`
    :raises NoSuchObjectError: If the exception type is `NoSuchObjectErrorBase`
    :raises PacketError: If the exception type is `PacketErrorBase`
    :raises ParseError: If the exception type is `ParseErrorBase`
    :raises TimeoutError: If the exception type is `TimeoutErrorBase`
    :raises UndeterminedTypeError: If the exception type is `UndeterminedTypeErrorBase`
    :raises UnknownObjectIDError: If the exception type is `UnknownObjectIDErrorBase`
    :raises Exception: If the exception type does not match any of the above

    Example:
        >>> from ezsnmp.netsnmp import snmpbulkget
        >>> NETSNMP_SESS_V2_ARGS = ["-v", "2c", "-c", "public", "localhost:11161"]
        >>> netsnmp_args = NETSNMP_SESS_V2_ARGS + [".iso.org.dod.internet.mgmt.mib-2.system.sysDescr.0"]
        >>> result = snmpbulkget(netsnmp_args)
        >>> print("OID:", result.oid)
        >>> print("Index:", result.index)
        >>> print("Value:", result.value)
        >>> print("Type:", result.type)
    """
    try:
        result = netsnmp_snmpbulkget(netsnmp_args)
        return result
    except Exception as e:
        _handle_error(e)


def snmpbulkwalk(netsnmp_args=[]):
    """
    Perform an SNMP BULKWALK operation using the provided arguments.

    This function uses the `netsnmp_snmpbulkwalk` function to perform an SNMP BULKWALK
    operation and returns the result.

    :param netsnmp_args: The arguments required for the SNMP BULKWALK operation
    :type netsnmp_args: list
    :return: A tuple of Result objects containing SNMP variable bindings. Each Result object has
            attributes: oid (str), index (str), value (str), and type (str)
    :rtype: tuple[Result]

    :raises ConnectionError: If the exception type is `ConnectionErrorBase`
    :raises GenericError: If the exception type is `GenericErrorBase`
    :raises NoSuchInstanceError: If the exception type is `NoSuchInstanceErrorBase`
    :raises NoSuchNameError: If the exception type is `NoSuchNameErrorBase`
    :raises NoSuchObjectError: If the exception type is `NoSuchObjectErrorBase`
    :raises PacketError: If the exception type is `PacketErrorBase`
    :raises ParseError: If the exception type is `ParseErrorBase`
    :raises TimeoutError: If the exception type is `TimeoutErrorBase`
    :raises UndeterminedTypeError: If the exception type is `UndeterminedTypeErrorBase`
    :raises UnknownObjectIDError: If the exception type is `UnknownObjectIDErrorBase`
    :raises Exception: If the exception type does not match any of the above

    Example:
        >>> from ezsnmp.netsnmp import snmpbulkwalk
        >>> NETSNMP_SESS_V2_ARGS = ["-v", "2c", "-c", "public", "localhost:11161"]
        >>> netsnmp_args = NETSNMP_SESS_V2_ARGS + [".iso.org.dod.internet.mgmt.mib-2.system.sysDescr"]
        >>> result = snmpbulkwalk(netsnmp_args)
        >>> print("OID:", result.oid)
        >>> print("Index:", result.index)
        >>> print("Value:", result.value)
        >>> print("Type:", result.type)
    """
    try:
        result = netsnmp_snmpbulkwalk(netsnmp_args)
        return result
    except Exception as e:
        _handle_error(e)


def snmpset(netsnmp_args=[]):
    """
    Perform an SNMP SET operation using the provided arguments.

    This function uses the `netsnmp_snmpset` function to perform an SNMP SET
    operation and returns the result.

    :param netsnmp_args: The arguments required for the SNMP SET operation
    :type netsnmp_args: list
    :return: A tuple of Result objects containing SNMP variable bindings. Each Result object has
            attributes: oid (str), index (str), value (str), and type (str)
    :rtype: tuple[Result]

    :raises ConnectionError: If the exception type is `ConnectionErrorBase`
    :raises GenericError: If the exception type is `GenericErrorBase`
    :raises NoSuchInstanceError: If the exception type is `NoSuchInstanceErrorBase`
    :raises NoSuchNameError: If the exception type is `NoSuchNameErrorBase`
    :raises NoSuchObjectError: If the exception type is `NoSuchObjectErrorBase`
    :raises PacketError: If the exception type is `PacketErrorBase`
    :raises ParseError: If the exception type is `ParseErrorBase`
    :raises TimeoutError: If the exception type is `TimeoutErrorBase`
    :raises UndeterminedTypeError: If the exception type is `UndeterminedTypeErrorBase`
    :raises UnknownObjectIDError: If the exception type is `UnknownObjectIDErrorBase`
    :raises Exception: If the exception type does not match any of the above

    Example:
        >>> from ezsnmp.netsnmp import snmpset
        >>> NETSNMP_SESS_V2_ARGS = ["-v", "2c", "-c", "public", "localhost:11161"]
        >>> netsnmp_args = NETSNMP_SESS_V2_ARGS + [".iso.org.dod.internet.mgmt.mib-2.system.sysContact.0", "s", "admin@example.com"]
        >>> result = snmpset(netsnmp_args)
        >>> print("OID:", result.oid)
        >>> print("Index:", result.index)
        >>> print("Value:", result.value)
        >>> print("Type:", result.type)
    """
    try:
        result = netsnmp_snmpset(netsnmp_args)
        return result
    except Exception as e:
        _handle_error(e)


def snmptrap(netsnmp_args=[]):
    """
    Perform an SNMP TRAP operation using the provided arguments.

    This function uses the `netsnmp_snmptrap` function to perform an SNMP TRAP
    operation and returns the result.

    :param netsnmp_args: The arguments required for the SNMP TRAP operation
    :type netsnmp_args: list
    :return: A tuple of Result objects containing SNMP variable bindings. Each Result object has
            attributes: oid (str), index (str), value (str), and type (str)
    :rtype: tuple[Result]

    :raises ConnectionError: If the exception type is `ConnectionErrorBase`
    :raises GenericError: If the exception type is `GenericErrorBase`
    :raises NoSuchInstanceError: If the exception type is `NoSuchInstanceErrorBase`
    :raises NoSuchNameError: If the exception type is `NoSuchNameErrorBase`
    :raises NoSuchObjectError: If the exception type is `NoSuchObjectErrorBase`
    :raises PacketError: If the exception type is `PacketErrorBase`
    :raises ParseError: If the exception type is `ParseErrorBase`
    :raises TimeoutError: If the exception type is `TimeoutErrorBase`
    :raises UndeterminedTypeError: If the exception type is `UndeterminedTypeErrorBase`
    :raises UnknownObjectIDError: If the exception type is `UnknownObjectIDErrorBase`
    :raises Exception: If the exception type does not match any of the above

    Example:
        >>> from ezsnmp.netsnmp import snmptrap
        >>> NETSNMP_SESS_V2_ARGS = ["-v", "2c", "-c", "public", "localhost:11162"]
        >>> netsnmp_args = NETSNMP_SESS_V2_ARGS + ["'' .1.3.6.1.6.3.1.1.5.1 0"]
        >>> result = snmptrap(netsnmp_args)
        >>> print("OID:", result.oid)
        >>> print("Index:", result.index)
        >>> print("Value:", result.value)
        >>> print("Type:", result.type)
    """
    try:
        result = netsnmp_snmptrap(netsnmp_args)
        return result
    except Exception as e:
        _handle_error(e)


# UPDATE THIS ONE NEXT WITH EXAMPLES LIKE YOU DID IN SESSION
