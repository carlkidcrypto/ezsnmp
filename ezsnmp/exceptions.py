class ConnectionError(Exception):
    def __init__(self, message):
        super().__init__(message)


class GenericError(Exception):
    def __init__(self, message):
        super().__init__(message)


class NoSuchInstanceError(Exception):
    def __init__(self, message):
        super().__init__(message)


class NoSuchNameError(Exception):
    def __init__(self, message):
        super().__init__(message)


class NoSuchObjectError(Exception):
    def __init__(self, message):
        super().__init__(message)


class PacketError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ParseError(Exception):
    def __init__(self, message):
        super().__init__(message)


class TimeoutError(Exception):
    def __init__(self, message):
        super().__init__(message)


class UndeterminedTypeError(Exception):
    def __init__(self, message):
        super().__init__(message)


class UnknownObjectIDError(Exception):
    def __init__(self, message):
        super().__init__(message)
