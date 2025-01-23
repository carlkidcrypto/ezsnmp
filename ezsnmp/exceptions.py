from .exceptionsbase import (
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


class GenericError(Exception):
    """
    A generic error for the ezsnmp library.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message=""):
        super().__init__(message)


class ConnectionError(GenericError):
    """
    An error indicating a connection issue.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message=""):
        super().__init__(message)


class TimeoutError(GenericError):
    """
    An error indicating a timeout.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message=""):
        super().__init__(message)


class UnknownObjectIDError(GenericError):
    """
    An error indicating an unknown object ID.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message=""):
        super().__init__(message)


class NoSuchNameError(GenericError):
    """
    An error indicating that no such name exists.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message=""):
        super().__init__(message)


class NoSuchObjectError(GenericError):
    """
    An error indicating that no such object exists.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message=""):
        super().__init__(message)


class NoSuchInstanceError(GenericError):
    """
    An error indicating that no such instance exists.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message=""):
        super().__init__(message)


class UndeterminedTypeError(GenericError):
    """
    An error indicating an undetermined type.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message=""):
        super().__init__(message)


class ParseError(GenericError):
    """
    An error indicating a parsing issue.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message=""):
        super().__init__(message)


class PacketError(GenericError):
    """
    An error indicating a packet issue.

    :param message: The error message.
    :type message: str
    """

    def __init__(self, message=""):
        super().__init__(message)
