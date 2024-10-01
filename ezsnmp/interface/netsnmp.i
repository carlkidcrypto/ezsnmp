%module netsnmp
%feature("autodoc", "0");

%include "stl.i"

// Tell SWIG how to handle our special return type from C++
%template(_string_list) std::vector<std::string>;

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
%include "snmpwalk.i"
%include "snmpset.i"