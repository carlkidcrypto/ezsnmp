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

class GenericError(Exception):
    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], GenericErrorBase):
            super().__init__(*args[1:], **kwargs)
            self.__cause__ = args[0]
        else:
            super().__init__(*args, **kwargs)

class ConnectionError(Exception):
    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], ConnectionErrorBase):
            super().__init__(*args[1:], **kwargs)
            self.__cause__ = args[0]
        else:
            super().__init__(*args, **kwargs)

class TimeoutError(Exception):
    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], TimeoutErrorBase):
            super().__init__(*args[1:], **kwargs)
            self.__cause__ = args[0]
        else:
            super().__init__(*args, **kwargs)

class UnknownObjectIDError(Exception):
    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], UnknownObjectIDErrorBase):
            super().__init__(*args[1:], **kwargs)
            self.__cause__ = args[0]
        else:
            super().__init__(*args, **kwargs)

class NoSuchNameError(Exception):
    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], NoSuchNameErrorBase):
            super().__init__(*args[1:], **kwargs)
            self.__cause__ = args[0]
        else:
            super().__init__(*args, **kwargs)

class NoSuchObjectError(Exception):
    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], NoSuchObjectErrorBase):
            super().__init__(*args[1:], **kwargs)
            self.__cause__ = args[0]
        else:
            super().__init__(*args, **kwargs)

class NoSuchInstanceError(Exception):
    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], NoSuchInstanceErrorBase):
            super().__init__(*args[1:], **kwargs)
            self.__cause__ = args[0]
        else:
            super().__init__(*args, **kwargs)

class UndeterminedTypeError(Exception):
    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], UndeterminedTypeErrorBase):
            super().__init__(*args[1:], **kwargs)
            self.__cause__ = args[0]
        else:
            super().__init__(*args, **kwargs)

class ParseError(Exception):
    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], ParseErrorBase):
            super().__init__(*args[1:], **kwargs)
            self.__cause__ = args[0]
        else:
            super().__init__(*args, **kwargs)

class PacketError(Exception):
    def __init__(self, *args, **kwargs):
        if args and isinstance(args[0], PacketErrorBase):
            super().__init__(*args[1:], **kwargs)
            self.__cause__ = args[0]
        else:
            super().__init__(*args, **kwargs)