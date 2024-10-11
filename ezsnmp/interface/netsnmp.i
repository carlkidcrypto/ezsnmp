%module netsnmp
%feature("autodoc", "0");

%include "stl.i"
%include "datatypes.i"

%feature("python:annotations", "c");

// Tell SWIG how to handle our special return type(s) from C++
%template(_string_list) std::vector<std::string>;
%template(_result_list) std::vector<Result>;

// Typemaps for std::vector<std::string>

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

// Tell SWIG we want C++ errors converted to proper high-level language errors
%exception {
    try {
        $action
    } catch (const std::runtime_error& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        SWIG_fail;
    }
};

%include "snmpbulkget.i"
%include "snmpbulkwalk.i"
%include "snmpget.i"
%include "snmpset.i"
%include "snmptrap.i"
%include "snmpwalk.i"