from .exceptionsbase import (
    GenericErrorBase,
    ConnectionErrorBase,
    TimeoutErrorBase,
    UnknownObjectIDErrorBase,
    NoSuchNameErrorBase,
    NoSuchObjectErrorBase,
    NoSuchInstanceErrorBase,
    UndeterminedTypeErrorBase,
    ParseErrorBase,
    PacketErrorBase,
)

class _HiddenBase(GenericErrorBase): 
    class GenericError(Exception):
        """
        A generic error for the ezsnmp library.

        :param message: The error message.
        :type message: str
        """
        def __init__(self, message=""):
            super().__init__(message)
GenericError = _HiddenBase.GenericError

class _HiddenBase(ConnectionErrorBase): 
    class ConnectionError(Exception):
        """
        An error indicating a connection issue.

        :param message: The error message.
        :type message: str
        """
        def __init__(self, message=""):
            super().__init__(message)
ConnectionError = _HiddenBase.ConnectionError

class _HiddenBase(TimeoutErrorBase): 
    class TimeoutError(Exception):
        """
        An error indicating a timeout.

        :param message: The error message.
        :type message: str
        """
        def __init__(self, message=""):
            super().__init__(message)
TimeoutError = _HiddenBase.TimeoutError

class _HiddenBase(UnknownObjectIDErrorBase): 
    class UnknownObjectIDError(Exception):
        """
        An error indicating an unknown object ID.

        :param message: The error message.
        :type message: str
        """
        def __init__(self, message=""):
            super().__init__(message)
UnknownObjectIDError = _HiddenBase.UnknownObjectIDError

class _HiddenBase(NoSuchNameErrorBase): 
    class NoSuchNameError(Exception):
        """
        An error indicating that no such name exists.

        :param message: The error message.
        :type message: str
        """
        def __init__(self, message=""):
            super().__init__(message)
NoSuchNameError = _HiddenBase.NoSuchNameError

class _HiddenBase(NoSuchObjectErrorBase): 
    class NoSuchObjectError(Exception):
        """
        An error indicating that no such object exists.

        :param message: The error message.
        :type message: str
        """
        def __init__(self, message=""):
            super().__init__(message)
NoSuchObjectError = _HiddenBase.NoSuchObjectError

class _HiddenBase(NoSuchInstanceErrorBase): 
    class NoSuchInstanceError(Exception):
        """
        An error indicating that no such instance exists.

        :param message: The error message.
        :type message: str
        """
        def __init__(self, message=""):
            super().__init__(message)
NoSuchInstanceError = _HiddenBase.NoSuchInstanceError

class _HiddenBase(UndeterminedTypeErrorBase): 
    class UndeterminedTypeError(Exception):
        """
        An error indicating an undetermined type.

        :param message: The error message.
        :type message: str
        """
        def __init__(self, message=""):
            super().__init__(message)
UndeterminedTypeError = _HiddenBase.UndeterminedTypeError

class _HiddenBase(ParseErrorBase): 
    class ParseError(Exception):
        """
        An error indicating a parsing issue.

        :param message: The error message.
        :type message: str
        """
        def __init__(self, message=""):
            super().__init__(message)
ParseError = _HiddenBase.ParseError

class _HiddenBase(PacketErrorBase): 
    class PacketError(Exception):
        """
        An error indicating a packet issue.

        :param message: The error message.
        :type message: str
        """
        def __init__(self, message=""):
            super().__init__(message)
PacketError = _HiddenBase.PacketError