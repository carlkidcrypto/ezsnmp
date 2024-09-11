# This file was automatically generated by SWIG (https://www.swig.org).
# Version 4.2.1
#
# Do not make changes to this file unless you know what you are doing - modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
# Import the low-level C/C++ module
if __package__ or "." in __name__:
    from . import _ezsnmp_swig
else:
    import _ezsnmp_swig

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)


def _swig_setattr_nondynamic_instance_variable(set):
    def set_instance_attr(self, name, value):
        if name == "this":
            set(self, name, value)
        elif name == "thisown":
            self.this.own(value)
        elif hasattr(self, name) and isinstance(getattr(type(self), name), property):
            set(self, name, value)
        else:
            raise AttributeError("You cannot add instance attributes to %s" % self)
    return set_instance_attr


def _swig_setattr_nondynamic_class_variable(set):
    def set_class_attr(cls, name, value):
        if hasattr(cls, name) and not isinstance(getattr(cls, name), property):
            set(cls, name, value)
        else:
            raise AttributeError("You cannot add class attributes to %s" % cls)
    return set_class_attr


def _swig_add_metaclass(metaclass):
    """Class decorator for adding a metaclass to a SWIG wrapped class - a slimmed down version of six.add_metaclass"""
    def wrapper(cls):
        return metaclass(cls.__name__, cls.__bases__, cls.__dict__.copy())
    return wrapper


class _SwigNonDynamicMeta(type):
    """Meta class to enforce nondynamic attributes (no new attributes) for a class"""
    __setattr__ = _swig_setattr_nondynamic_class_variable(type.__setattr__)



def snmpbulkget_usage():
    return _ezsnmp_swig.snmpbulkget_usage()

def snmpbulkget_optProc(argc, argv, opt):
    return _ezsnmp_swig.snmpbulkget_optProc(argc, argv, opt)

def snmpbulkget(argc, argv):
    return _ezsnmp_swig.snmpbulkget(argc, argv)

def snmpbulkwalk_usage():
    return _ezsnmp_swig.snmpbulkwalk_usage()

def snmpbulkwalk_optProc(argc, argv, opt):
    return _ezsnmp_swig.snmpbulkwalk_optProc(argc, argv, opt)

def snmpbulkwalk(argc):
    return _ezsnmp_swig.snmpbulkwalk(argc)

def snmpget_usage():
    return _ezsnmp_swig.snmpget_usage()

def snmpget_optProc(argc, argv, opt):
    return _ezsnmp_swig.snmpget_optProc(argc, argv, opt)

def snmpget(argc):
    return _ezsnmp_swig.snmpget(argc)

def snmpwalk_usage():
    return _ezsnmp_swig.snmpwalk_usage()

def snmpwalk_snmp_get_and_print(ss, theoid, theoid_len):
    return _ezsnmp_swig.snmpwalk_snmp_get_and_print(ss, theoid, theoid_len)

def snmpwalk_optProc(argc, argv, opt):
    return _ezsnmp_swig.snmpwalk_optProc(argc, argv, opt)

def snmpwalk(argc):
    return _ezsnmp_swig.snmpwalk(argc)

