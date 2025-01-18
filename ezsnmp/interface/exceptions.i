%module exceptions
%feature("autodoc", "0");

%include "stl.i"

%{
#include "exceptions.h"
%}

// Tell SWIG we want C++ errors converted to proper high-level language errors
%exception {
    try {
        $action
    } catch (const EzSnmpConnectionError& e) {
        PyErr_SetString(EzSnmpConnectionError_type, e.what());
        SWIG_fail;
    } catch (const EzSnmpTimeoutError& e) {
        PyErr_SetString(EzSnmpTimeoutError_type, e.what());
        SWIG_fail;
    } catch (const EzSnmpUnknownObjectIDError& e) {
        PyErr_SetString(EzSnmpUnknownObjectIDError_type, e.what());
        SWIG_fail;
    } catch (const EzSnmpNoSuchNameError& e) {
        PyErr_SetString(EzSnmpNoSuchNameError_type, e.what());
        SWIG_fail;
    } catch (const EzSnmpNoSuchObjectError& e) {
        PyErr_SetString(EzSnmpNoSuchObjectError_type, e.what());
        SWIG_fail;
    } catch (const EzSnmpNoSuchInstanceError& e) {
        PyErr_SetString(EzSnmpNoSuchInstanceError_type, e.what());
        SWIG_fail;
    } catch (const EzSnmpUndeterminedTypeError& e) {
        PyErr_SetString(EzSnmpUndeterminedTypeError_type, e.what());
        SWIG_fail;
    } catch (const std::runtime_error& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        SWIG_fail;
    } catch (const std::invalid_argument& e) {
        PyErr_SetString(PyExc_ValueError, e.what());
        SWIG_fail;
    }
};

// Include the header file
%include "../include/exceptions.h"