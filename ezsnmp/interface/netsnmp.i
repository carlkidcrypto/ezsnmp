%module netsnmp
%feature("autodoc", "0");

%include "stl.i"
%include "datatypes.i"

%feature("python:annotations", "c");

// Tell SWIG how to handle our special return type(s) from C++
%template(_string_list) std::vector<std::string>;
%template(_result_list) std::vector<Result>;

// Tell SWIG we want C++ errors converted to proper high-level language errors
%exception {
    try {
        $action
    } catch (const std::runtime_error& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        SWIG_fail;
    }
};

%typemap(out) std::vector<std::string> {
  $result = PyList_New($1.size());
  for (size_t i = 0; i < $1.size(); ++i) {
    PyObject* str = PyUnicode_FromString($1[i].c_str());
    PyList_SET_ITEM($result, i, str); 
  }
}

%include "snmpbulkget.i"
%include "snmpbulkwalk.i"
%include "snmpget.i"
%include "snmpset.i"
%include "snmptrap.i"
%include "snmpwalk.i"