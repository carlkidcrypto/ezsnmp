%module exceptions
%feature("autodoc", "0");

%{
#include "exceptions.h"
%}

%include <std_string.i>
%include <std_except.i> 

// Tell SWIG we want C++ errors converted to proper high-level language errors
%exception {
    try {
        $action
    } catch (const EzSnmpConnectionError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_EzSnmpConnectionError), e.what());
    SWIG_fail;
    } catch (const EzSnmpTimeoutError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_EzSnmpTimeoutError), e.what());
    SWIG_fail;
    } catch (const EzSnmpUnknownObjectIDError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_EzSnmpUnknownObjectIDError), e.what());
    SWIG_fail;
    } catch (const EzSnmpNoSuchNameError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_EzSnmpNoSuchNameError), e.what());
    SWIG_fail;
    } catch (const EzSnmpNoSuchObjectError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_EzSnmpNoSuchObjectError), e.what());
    SWIG_fail;
    } catch (const EzSnmpNoSuchInstanceError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_EzSnmpNoSuchInstanceError), e.what());
    SWIG_fail;
    } catch (const EzSnmpUndeterminedTypeError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_EzSnmpUndeterminedTypeError), e.what());
    SWIG_fail;
    } catch (const std::runtime_error& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    SWIG_fail;
    } catch (const std::invalid_argument& e) {
    PyErr_SetString(PyExc_ValueError, e.what());
    SWIG_fail;
    }
};

%exceptionclass EzSnmpError;
%exceptionclass EzSnmpConnectionError;
%exceptionclass EzSnmpTimeoutError;
%exceptionclass EzSnmpUnknownObjectIDError;
%exceptionclass EzSnmpNoSuchNameError;
%exceptionclass EzSnmpNoSuchObjectError;
%exceptionclass EzSnmpNoSuchInstanceError;
%exceptionclass EzSnmpUndeterminedTypeError;

// Include the header file
%include "../include/exceptions.h"