%module exceptions
%feature("autodoc", "0");

%include "stl.i"

%{
#include "exceptions.h"
%}

%init %{
    // Initialize exception types
    EzSnmpError_type = PyErr_NewException("exceptions.EzSnmpError", NULL, NULL);
    if (EzSnmpError_type == NULL) {
        return NULL; 
    }
    Py_INCREF(EzSnmpError_type);
    PyModule_AddObject(m, "EzSnmpError", EzSnmpError_type);

    EzSnmpConnectionError_type = PyErr_NewException("exceptions.EzSnmpConnectionError", EzSnmpError_type, NULL);
    if (EzSnmpConnectionError_type == NULL) {
        return NULL; 
    }
    Py_INCREF(EzSnmpConnectionError_type);
    PyModule_AddObject(m, "EzSnmpConnectionError", EzSnmpConnectionError_type);

    EzSnmpTimeoutError_type = PyErr_NewException("exceptions.EzSnmpTimeoutError", EzSnmpError_type, NULL);
    if (EzSnmpTimeoutError_type == NULL) {
        return NULL; 
    }
    Py_INCREF(EzSnmpTimeoutError_type);
    PyModule_AddObject(m, "EzSnmpTimeoutError", EzSnmpTimeoutError_type);

    EzSnmpUnknownObjectIDError_type = PyErr_NewException("exceptions.EzSnmpUnknownObjectIDError", EzSnmpError_type, NULL);
    if (EzSnmpUnknownObjectIDError_type == NULL) {
        return NULL; 
    }
    Py_INCREF(EzSnmpUnknownObjectIDError_type);
    PyModule_AddObject(m, "EzSnmpUnknownObjectIDError", EzSnmpUnknownObjectIDError_type);

    EzSnmpNoSuchNameError_type = PyErr_NewException("exceptions.EzSnmpNoSuchNameError", EzSnmpError_type, NULL);
    if (EzSnmpNoSuchNameError_type == NULL) {
        return NULL; 
    }
    Py_INCREF(EzSnmpNoSuchNameError_type);
    PyModule_AddObject(m, "EzSnmpNoSuchNameError", EzSnmpNoSuchNameError_type);

    EzSnmpNoSuchObjectError_type = PyErr_NewException("exceptions.EzSnmpNoSuchObjectError", EzSnmpError_type, NULL);
    if (EzSnmpNoSuchObjectError_type == NULL) {
        return NULL; 
    }
    Py_INCREF(EzSnmpNoSuchObjectError_type);
    PyModule_AddObject(m, "EzSnmpNoSuchObjectError", EzSnmpNoSuchObjectError_type);

    EzSnmpNoSuchInstanceError_type = PyErr_NewException("exceptions.EzSnmpNoSuchInstanceError", EzSnmpError_type, NULL);
    if (EzSnmpNoSuchInstanceError_type == NULL) {
        return NULL; 
    }
    Py_INCREF(EzSnmpNoSuchInstanceError_type);
    PyModule_AddObject(m, "EzSnmpNoSuchInstanceError", EzSnmpNoSuchInstanceError_type);

    EzSnmpUndeterminedTypeError_type = PyErr_NewException("exceptions.EzSnmpUndeterminedTypeError", EzSnmpError_type, NULL);
    if (EzSnmpUndeterminedTypeError_type == NULL) {
        return NULL; 
    }
    Py_INCREF(EzSnmpUndeterminedTypeError_type);
    PyModule_AddObject(m, "EzSnmpUndeterminedTypeError", EzSnmpUndeterminedTypeError_type);
%}

// Include the header file
%include "../include/exceptions.h"

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