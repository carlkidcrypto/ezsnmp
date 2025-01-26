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
