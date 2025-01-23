%module exceptionsbase
%feature("autodoc", "0");

%{
#include "exceptionsbase.h"
%}

%include <std_string.i>
%include <std_except.i> 

// Tell SWIG we want C++ errors converted to proper high-level language errors
%exception {
    try {
        $action
    } catch (const ConnectionErrorBase& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_ConnectionErrorBase), e.what());
    SWIG_fail;
    } catch (const TimeoutErrorBase& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_TimeoutErrorBase), e.what());
    SWIG_fail;
    } catch (const UnknownObjectIDErrorBase& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_UnknownObjectIDErrorBase), e.what());
    SWIG_fail;
    } catch (const NoSuchNameErrorBase& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_NoSuchNameErrorBase), e.what());
    SWIG_fail;
    } catch (const NoSuchObjectErrorBase& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_NoSuchObjectErrorBase), e.what());
    SWIG_fail;
    } catch (const NoSuchInstanceErrorBase& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_NoSuchInstanceErrorBase), e.what());
    SWIG_fail;
    } catch (const UndeterminedTypeErrorBase& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_UndeterminedTypeErrorBase), e.what());
    SWIG_fail;
    } catch (const ParseErrorBase& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_ParseErrorBase), e.what());
    SWIG_fail;
    }catch (const PacketErrorBase& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_PacketErrorBase), e.what());
    SWIG_fail;
    }catch (const GenericErrorBase& e) {
    PyErr_SetString(SWIG_Python_ExceptionType(SWIGTYPE_p_GenericErrorBase), e.what());
    SWIG_fail;
    }
};

%exceptionclass GenericErrorBase;
%exceptionclass ConnectionErrorBase;
%exceptionclass TimeoutErrorBase;
%exceptionclass UnknownObjectIDErrorBase;
%exceptionclass NoSuchNameErrorBase;
%exceptionclass NoSuchObjectErrorBase;
%exceptionclass NoSuchInstanceErrorBase;
%exceptionclass UndeterminedTypeErrorBase;
%exceptionclass ParseErrorBase;
%exceptionclass PacketErrorBase;

// Include the header file
%include "../include/exceptionsbase.h"