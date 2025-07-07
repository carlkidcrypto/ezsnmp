from .datatypesbase import ResultBase


class Result():
    """
    Result class for SNMP operations.

    This class is used to represent the result of an SNMP operation, including
    the OID, value, and any error status.
    """

    def __init__(self, result_base: ResultBase):
        self._oid = result_base.oid
        self._index = result_base.index
        self._type = result_base.type
        self._value = result_base.value

        print(self._oid, self._index, self._type, self._value)

        result_base.update_converted_value()
        temp1 = result_base._get_converted_value_int()
        temp2 = result_base._get_converted_value_uint32()
        temp3 = result_base._get_converted_value_uint64()
        temp4 = result_base._get_converted_value_double()

        print(temp1, temp2, temp3, temp4)
    
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