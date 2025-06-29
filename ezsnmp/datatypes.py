from .datatypesbase import ResultBase


class Result(ResultBase):
    """
    Result class for SNMP operations, inheriting from ResultBase.

    This class is used to represent the result of an SNMP operation, including
    the OID, value, and any error status.
    """

    def __init__(self, result_base: ResultBase):
        self._oid = result_base.oid
        self._index = result_base.index
        self._type = result_base.type
        self._value = result_base.value

        temp1 = result_base._get_converted_value_int()
        temp2 = result_base._get_converted_value_uint32()
        temp3 = result_base._get_converted_value_uint64()
        temp4 = result_base._get_converted_value_double()

        def try_get(opt):
            print("All attributes of opt:", dir(opt))
            return opt.contents() if hasattr(opt, "has_contents") and opt.has_contents() else None

        print(try_get(temp1), try_get(temp2), try_get(temp3), try_get(temp4))

        self._converted_value = None

    @property
    def oid(self):
        return self._oid

    @oid.setter
    def oid(self, value):
        self._oid = value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def converted_value(self):
        return self._converted_value

    @converted_value.setter
    def converted_value(self, value):
        self._converted_value = value

    def to_string(self):
        return self._to_string()