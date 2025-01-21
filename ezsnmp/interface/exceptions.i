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
    } catch (const ConnectionError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_ConnectionError), e.what());
    SWIG_fail;
    } catch (const TimeoutError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_TimeoutError), e.what());
    SWIG_fail;
    } catch (const UnknownObjectIDError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_UnknownObjectIDError), e.what());
    SWIG_fail;
    } catch (const NoSuchNameError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_NoSuchNameError), e.what());
    SWIG_fail;
    } catch (const NoSuchObjectError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_NoSuchObjectError), e.what());
    SWIG_fail;
    } catch (const NoSuchInstanceError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_NoSuchInstanceError), e.what());
    SWIG_fail;
    } catch (const UndeterminedTypeError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_UndeterminedTypeError), e.what());
    SWIG_fail;
    } catch (const ParseError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_ParseError), e.what());
    SWIG_fail;
    }catch (const PacketError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_PacketError), e.what());
    SWIG_fail;
    }catch (const std::runtime_error& e) {
    PyErr_SetString(PyExc_RuntimeError, e.what());
    SWIG_fail;
    } catch (const std::invalid_argument& e) {
    PyErr_SetString(PyExc_ValueError, e.what());
    SWIG_fail;
    }catch (const GenericError& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_GenericError), e.what());
    SWIG_fail;
    }
};

%exceptionclass GenericError;
%exceptionclass ConnectionError;
%exceptionclass TimeoutError;
%exceptionclass UnknownObjectIDError;
%exceptionclass NoSuchNameError;
%exceptionclass NoSuchObjectError;
%exceptionclass NoSuchInstanceError;
%exceptionclass UndeterminedTypeError;
%exceptionclass ParseError;
%exceptionclass PacketError;

// Include the header file
%include "../include/exceptions.h"