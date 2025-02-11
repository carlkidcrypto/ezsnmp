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


def snmpget(netsnmp_args):
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


def snmpgetnext(netsnmp_args):
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


def snmpwalk(netsnmp_args):
    """
    Perform an SNMP walk operation using the provided arguments.

    This function uses the `netsnmp_snmpwalk` function to perform an SNMP walk
    and returns the result. If an exception occurs during the operation, it
    handles the error using the `_handle_error` function.

    :param netsnmp_args: The arguments required for the SNMP walk operation.
    :type netsnmp_args: dict
    :return: The result of the SNMP walk operation.
    :rtype: list
    :raises Exception: If an error occurs during the SNMP walk operation.
    """
    try:
        result = netsnmp_snmpwalk(netsnmp_args)
        return result
    except Exception as e:
        _handle_error(e)


def snmpbulkget(netsnmp_args):
    """
    Perform an SNMP bulk get operation using the provided arguments.

    This function wraps the `netsnmp_snmpbulkget` function and handles any exceptions
    that may occur during the operation.

    :param netsnmp_args: The arguments required for the SNMP bulk get operation.
    :type netsnmp_args: dict or list
    :return: The result of the SNMP bulk get operation.
    :rtype: dict or list
    :raises Exception: If an error occurs during the SNMP bulk get operation.
    """
    try:
        result = netsnmp_snmpbulkget(netsnmp_args)
        return result
    except Exception as e:
        _handle_error(e)


def snmpbulkwalk(netsnmp_args):
    """
    Perform an SNMP bulk walk operation.

    This function uses the `netsnmp_snmpbulkwalk` function to perform an SNMP bulk walk
    based on the provided arguments. It returns the result of the bulk walk operation.

    :param netsnmp_args: The arguments required for the SNMP bulk walk operation.
    :type netsnmp_args: dict
    :return: The result of the SNMP bulk walk operation.
    :rtype: list
    :raises Exception: If an error occurs during the SNMP bulk walk operation.
    """
    try:
        result = netsnmp_snmpbulkwalk(netsnmp_args)
        return result
    except Exception as e:
        _handle_error(e)


def snmpset(netsnmp_args):
    """
    Perform an SNMP set operation using the provided arguments.

    This function attempts to set SNMP values based on the given arguments
    by calling the `netsnmp_snmpset` function. If an error occurs during
    the operation, it handles the exception by calling the `_handle_error` function.

    :param netsnmp_args: The arguments required for the SNMP set operation.
    :type netsnmp_args: dict
    :return: The result of the SNMP set operation.
    :rtype: Any
    :raises Exception: If an error occurs during the SNMP set operation.
    """
    try:
        result = netsnmp_snmpset(netsnmp_args)
        return result
    except Exception as e:
        _handle_error(e)


def snmptrap(netsnmp_args):
    """
    Send an SNMP trap using the provided Net-SNMP arguments.

    This function attempts to send an SNMP trap using the `netsnmp_snmptrap` function.
    If an exception occurs during the process, it handles the error using the `_handle_error` function.

    :param netsnmp_args: Arguments required by the Net-SNMP `snmptrap` command.
    :type netsnmp_args: list or str
    :raises Exception: If an error occurs during the SNMP trap operation.
    """
    try:
        result = netsnmp_snmptrap(netsnmp_args)
        return result
    except Exception as e:
        _handle_error(e)
