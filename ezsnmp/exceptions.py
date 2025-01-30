class ConnectionError(Exception):
    def __init__(self, message):
        """
        Exception raised for SNMP connection errors.

        This class represents an error that occurs during an SNMP connection attempt.

        :param message: A descriptive error message.
        :type message: str
        """
        super().__init__(message)


class GenericError(Exception):
    def __init__(self, message):
        """
        Exception raised for handling SNMP errors in the ezsnmp library.

        This class extends the standard Exception class to provide
        detailed error messages specific to SNMP operations.

        :param message: Explanation of the error.
        :type message: str
        """
        super().__init__(message)


class NoSuchInstanceError(Exception):
    def __init__(self, message):
        """
        Exception raised for handling SNMP "No Such Instance" errors.

        This exception is thrown when an SNMP operation encounters a "No Such Instance" error,
        indicating that the requested instance does not exist.

        :param message: Explanation of the error.
        :type message: str
        """
        super().__init__(message)


class NoSuchNameError(Exception):
    def __init__(self, message):
        """
        Exception raised for handling SNMP "No Such Name" errors.

        This class represents an error that occurs when an SNMP operation
        encounters a "No Such Name" error, indicating that the requested
        object does not exist.

        :param message: Explanation of the error.
        :type message: str
        """
        super().__init__(message)


class NoSuchObjectError(Exception):
    def __init__(self, message):
        """
        Exception raised for handling SNMP "No Such Object" errors.

        This exception is thrown when an SNMP operation encounters a "No Such Object" error.

        :param message: Explanation of the error.
        :type message: str
        """
        super().__init__(message)


class PacketError(Exception):
    def __init__(self, message):
        """
        Exception raised for handling SNMP packet errors.

        This exception is thrown when an error occurs related to SNMP packet processing.

        :param message: Explanation of the error.
        :type message: str
        """
        super().__init__(message)


class ParseError(Exception):
    def __init__(self, message):
        """
        Exception raised for handling SNMP parse errors.

        This exception is thrown when an error occurs while parsing SNMP command line arguments.

        :param message: Explanation of the error.
        :type message: str
        """
        super().__init__(message)


class TimeoutError(Exception):
    def __init__(self, message):
        """
        Exception raised for handling SNMP timeout errors.

        This class represents an error that occurs when an SNMP operation times out.

        :param message: A descriptive message about the timeout error.
        :type message: str
        """
        super().__init__(message)


class UndeterminedTypeError(Exception):
    def __init__(self, message):
        """
        Exception raised for undetermined SNMP type errors.

        This exception is thrown when an SNMP type cannot be determined.

        :param message: A descriptive error message.
        :type message: str
        """
        super().__init__(message)


class UnknownObjectIDError(Exception):
    def __init__(self, message):
        """
        Exception raised for unknown SNMP Object ID errors.

        This exception is thrown when an unknown SNMP Object ID is encountered.

        :param message: A string containing the error message.
        :type message: str
        """
        super().__init__(message)


def _handle_error(e):
    """
    Handle and map C++ error types to corresponding Python exceptions.

    This function inspects the type of the given exception `e` and raises
    a corresponding Python exception that can be caught. It maps various
    C++ error base types to custom Python exceptions.

    :param e: The exception object to be handled and mapped.
    :type e: Exception

    :raises ConnectionError: If the exception type is `ConnectionErrorBase`.
    :raises GenericError: If the exception type is `GenericErrorBase`.
    :raises NoSuchInstanceError: If the exception type is `NoSuchInstanceErrorBase`.
    :raises NoSuchNameError: If the exception type is `NoSuchNameErrorBase`.
    :raises NoSuchObjectError: If the exception type is `NoSuchObjectErrorBase`.
    :raises PacketError: If the exception type is `PacketErrorBase`.
    :raises ParseError: If the exception type is `ParseErrorBase`.
    :raises TimeoutError: If the exception type is `TimeoutErrorBase`.
    :raises UndeterminedTypeError: If the exception type is `UndeterminedTypeErrorBase`.
    :raises UnknownObjectIDError: If the exception type is `UnknownObjectIDErrorBase`.
    :raises Exception: If the exception type does not match any of the above, the original
                       exception `e` is raised.
    """

    if "ConnectionErrorBase" in str(type(e)):
        raise ConnectionError(str(e))
    elif "GenericErrorBase" in str(type(e)):
        raise GenericError(str(e))
    elif "NoSuchInstanceErrorBase" in str(type(e)):
        raise NoSuchInstanceError(str(e))
    elif "NoSuchNameErrorBase" in str(type(e)):
        raise NoSuchNameError(str(e))
    elif "NoSuchObjectErrorBase" in str(type(e)):
        raise NoSuchObjectError(str(e))
    elif "PacketErrorBase" in str(type(e)):
        raise PacketError(str(e))
    elif "ParseErrorBase" in str(type(e)):
        raise ParseError(str(e))
    elif "TimeoutErrorBase" in str(type(e)):
        raise TimeoutError(str(e))
    elif "UndeterminedTypeErrorBase" in str(type(e)):
        raise UndeterminedTypeError(str(e))
    elif "UnknownObjectIDErrorBase" in str(type(e)):
        raise UnknownObjectIDError(str(e))
    else:
        raise e
