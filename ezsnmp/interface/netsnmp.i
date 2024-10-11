%module netsnmp
%feature("autodoc", "0");

%include "stl.i"
%include "datatypes.i"

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
// Output typemap (std::vector<Result> to Python list of MappingProxyType objects)
%typemap(out) std::vector<Result> {
  $result = PyList_New($1.size());
  for (size_t i = 0; i < $1.size(); ++i) {
    PyObject *dict = PyDict_New();

    // Use PyUnicode_FromString to create Python Unicode objects
    PyDict_SetItemString(dict, "oid", PyUnicode_FromString($1[i].oid.c_str()));  // Use $1[i]
    PyDict_SetItemString(dict, "index", PyUnicode_FromString($1[i].index.c_str()));  // Use $1[i]
    PyDict_SetItemString(dict, "type", PyUnicode_FromString($1[i].type.c_str()));  // Use $1[i]
    PyDict_SetItemString(dict, "value", PyUnicode_FromString($1[i].value.c_str()));  // Use $1[i]

    // Import the types module
    PyObject* types_module = PyImport_ImportModule("types"); 
    if (types_module == NULL) {
      PyErr_SetString(PyExc_ImportError, "Could not import 'types' module");
      SWIG_fail; 
    }

    // Get MappingProxyType from the types module
    PyObject* mappingproxy_type = PyObject_GetAttrString(types_module, "MappingProxyType"); 
    if (mappingproxy_type == NULL) {
      PyErr_SetString(PyExc_AttributeError, "Could not get 'MappingProxyType' from 'types' module");
      Py_DECREF(types_module);
      SWIG_fail; 
    }

    PyObject* immutable_dict = PyObject_CallFunctionObjArgs(mappingproxy_type, dict, NULL);

    PyList_SET_ITEM($result, i, immutable_dict); 

    Py_DECREF(types_module);
    Py_DECREF(mappingproxy_type); 
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

%include "snmpbulkget.i"
%include "snmpbulkwalk.i"
%include "snmpget.i"
%include "snmpset.i"
%include "snmptrap.i"
%include "snmpwalk.i"