%module exceptionsbase
%feature("autodoc", "0");

%{
#include "exceptionsbase.h"

static PyObject *pGenericErrorBase;
static PyObject *pConnectionErrorBase;
static PyObject *pTimeoutErrorBase;
static PyObject *pUnknownObjectIDErrorBase;
static PyObject *pNoSuchNameErrorBase;
static PyObject *pNoSuchObjectErrorBase;
static PyObject *pNoSuchInstanceErrorBase;
static PyObject *pUndeterminedTypeErrorBase;
static PyObject *pParseErrorBase;
static PyObject *pPacketErrorBase;
%}

%include <std_string.i>
%include <std_except.i> 


%init %{

pGenericErrorBase = PyErr_NewException("_exceptionsbase.GenericErrorBase", NULL, NULL);
Py_INCREF(pGenericErrorBase);
PyModule_AddObject(m, "GenericErrorBase", pGenericErrorBase);

pConnectionErrorBase = PyErr_NewException("_exceptionsbase.ConnectionErrorBase", pGenericErrorBase, NULL);
Py_INCREF(pConnectionErrorBase);
PyModule_AddObject(m, "ConnectionErrorBase", pConnectionErrorBase);

pTimeoutErrorBase = PyErr_NewException("_exceptionsbase.TimeoutErrorBase", pGenericErrorBase, NULL);
Py_INCREF(pTimeoutErrorBase);
PyModule_AddObject(m, "TimeoutErrorBase", pTimeoutErrorBase);

pUnknownObjectIDErrorBase = PyErr_NewException("_exceptionsbase.UnknownObjectIDErrorBase", pGenericErrorBase, NULL);
Py_INCREF(pUnknownObjectIDErrorBase);
PyModule_AddObject(m, "UnknownObjectIDErrorBase", pUnknownObjectIDErrorBase);

pNoSuchNameErrorBase = PyErr_NewException("_exceptionsbase.NoSuchNameErrorBase", pGenericErrorBase, NULL);
Py_INCREF(pNoSuchNameErrorBase);
PyModule_AddObject(m, "NoSuchNameErrorBase", pNoSuchNameErrorBase);

pNoSuchObjectErrorBase = PyErr_NewException("_exceptionsbase.NoSuchObjectErrorBase", pGenericErrorBase, NULL);
Py_INCREF(pNoSuchObjectErrorBase);
PyModule_AddObject(m, "NoSuchObjectErrorBase", pNoSuchObjectErrorBase);

pNoSuchInstanceErrorBase = PyErr_NewException("_exceptionsbase.NoSuchInstanceErrorBase", pGenericErrorBase, NULL);
Py_INCREF(pNoSuchInstanceErrorBase);
PyModule_AddObject(m, "NoSuchInstanceErrorBase", pNoSuchInstanceErrorBase);

pUndeterminedTypeErrorBase = PyErr_NewException("_exceptionsbase.UndeterminedTypeErrorBase", pGenericErrorBase, NULL);
Py_INCREF(pUndeterminedTypeErrorBase);
PyModule_AddObject(m, "UndeterminedTypeErrorBase", pUndeterminedTypeErrorBase);

pParseErrorBase = PyErr_NewException("_exceptionsbase.ParseErrorBase", pGenericErrorBase, NULL);
Py_INCREF(pParseErrorBase);
PyModule_AddObject(m, "ParseErrorBase", pParseErrorBase);

pPacketErrorBase = PyErr_NewException("_exceptionsbase.PacketErrorBase", pGenericErrorBase, NULL);
Py_INCREF(pPacketErrorBase);
PyModule_AddObject(m, "PacketErrorBase", pPacketErrorBase);
%}


// Tell SWIG we want C++ ErrorBases converted to proper high-level language ErrorBases
%exception {
    try {
    $action
    } catch (const ConnectionErrorBase& e) {
    PyErr_SetString(pConnectionErrorBase, const_cast<char*>(e.what()));
    SWIG_fail;
    } catch (const TimeoutErrorBase& e) {
    PyErr_SetString(pTimeoutErrorBase, const_cast<char*>(e.what()));
    SWIG_fail;
    } catch (const UnknownObjectIDErrorBase& e) {
    PyErr_SetString(pUnknownObjectIDErrorBase, const_cast<char*>(e.what()));
    SWIG_fail;
    } catch (const NoSuchNameErrorBase& e) {
    PyErr_SetString(pNoSuchNameErrorBase, const_cast<char*>(e.what()));
    SWIG_fail;
    } catch (const NoSuchObjectErrorBase& e) {
    PyErr_SetString(pNoSuchObjectErrorBase, const_cast<char*>(e.what()));
    SWIG_fail;
    } catch (const NoSuchInstanceErrorBase& e) {
    PyErr_SetString(pNoSuchInstanceErrorBase, const_cast<char*>(e.what()));
    SWIG_fail;
    } catch (const UndeterminedTypeErrorBase& e) {
    PyErr_SetString(pUndeterminedTypeErrorBase, const_cast<char*>(e.what()));
    SWIG_fail;
    } catch (const ParseErrorBase& e) {
    PyErr_SetString(pParseErrorBase, const_cast<char*>(e.what()));
    SWIG_fail;
    } catch (const PacketErrorBase& e) {
    PyErr_SetString(pPacketErrorBase, const_cast<char*>(e.what()));
    SWIG_fail;
    } catch (const GenericErrorBase& e) {
    PyErr_SetString(pGenericErrorBase, const_cast<char*>(e.what()));
    SWIG_fail;
    }
};

// Include the header file
%include "../include/exceptionsbase.h"