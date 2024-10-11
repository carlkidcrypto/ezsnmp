%module sessionbase
%feature("autodoc", "0");

%include "stl.i"
%include "datatypes.i"

%feature("kwargs") SessionBase::SessionBase;
%feature("python:annotations", "c");

// Tell SWIG how to handle our special return type(s) from C++
%template(_string_list) std::vector<std::string>;
%template(_result_list) std::vector<Result>;

// Typemaps for std::vector<std::string>: Added to support PyPy builds
// Input typemap (Python list to std::vector<std::string>)
%typemap(in) std::vector<std::string> (std::vector<std::string> temp) {
  if (!PyList_Check($input)) {
    PyErr_SetString(PyExc_TypeError, "Expected a list");
    SWIG_fail;
  }

  temp.resize(PyList_Size($input)); 
  for (size_t i = 0; i < PyList_Size($input); ++i) {
    PyObject* item = PyList_GetItem($input, i);
    if (!PyUnicode_Check(item)) {
      PyErr_SetString(PyExc_TypeError, "List items must be strings");
      SWIG_fail;
    }
    temp[i] = PyUnicode_AsUTF8(item); 
  }
  $1 = temp; 
}

// Output typemap (std::vector<std::string> to Python list)
%typemap(out) std::vector<std::string> {
  $result = PyList_New($1.size());
  for (size_t i = 0; i < $1.size(); ++i) {
    PyObject* str = PyUnicode_FromString($1[i].c_str());
    PyList_SET_ITEM($result, i, str); 
  }
}

// Typemaps for std::vector<Result>: Added to support PyPy builds
// Input typemap (Python list of dictionaries to std::vector<Result>)
%typemap(in) std::vector<Result> (std::vector<Result> temp) {
  if (!PyList_Check($input)) {
    PyErr_SetString(PyExc_TypeError, "Expected a list of dictionaries");
    SWIG_fail;
  }

  temp.resize(PyList_Size($input));
  for (size_t i = 0; i < PyList_Size($input); ++i) {
    PyObject* dict = PyList_GetItem($input, i);
    if (!PyDict_Check(dict)) {
      PyErr_SetString(PyExc_TypeError, "List items must be dictionaries");
      SWIG_fail;
    }

    // Extract values from the dictionary
    temp[i].oid = PyDict_GetItemString(dict, "oid") ? 
                   PyUnicode_AsUTF8(PyDict_GetItemString(dict, "oid")) : "";
    temp[i].index = PyDict_GetItemString(dict, "index") ? 
                     PyUnicode_AsUTF8(PyDict_GetItemString(dict, "index")) : "";
    temp[i].type = PyDict_GetItemString(dict, "type") ? 
                    PyUnicode_AsUTF8(PyDict_GetItemString(dict, "type")) : "";
    temp[i].value = PyDict_GetItemString(dict, "value") ? 
                     PyUnicode_AsUTF8(PyDict_GetItemString(dict, "value")) : "";
  }
  $1 = temp;
}

// Output typemap (std::vector<Result> to Python list of dictionaries)
%typemap(out) std::vector<Result> {
  $result = PyList_New($1.size());
  for (size_t i = 0; i < $1.size(); ++i) {
    PyObject* dict = PyDict_New();
    PyDict_SetItemString(dict, "oid", PyUnicode_AsUTF8($1[i].oid.c_str()));
    PyDict_SetItemString(dict, "index", PyUnicode_AsUTF8($1[i].index.c_str()));
    PyDict_SetItemString(dict, "type", PyUnicode_AsUTF8($1[i].type.c_str()));
    PyDict_SetItemString(dict, "value", PyUnicode_AsUTF8($1[i].value.c_str()));
    PyList_SET_ITEM($result, i, dict);
  }
}

// Tell SWIG we want C++ errors converted to proper high-level language errors
%exception {
    try {
        $action
    } catch (const std::runtime_error& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        SWIG_fail;
    } catch (const std::invalid_argument& e) {
        PyErr_SetString(PyExc_ValueError, e.what());
        SWIG_fail;
    }
};

%{
#include "sessionbase.h"
%}

// Now list ANSI C/C++ declarations
%include "../include/sessionbase.h"