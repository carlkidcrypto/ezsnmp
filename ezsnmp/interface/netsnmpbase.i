%module netsnmpbase
%feature("autodoc", "0");

%include <stl.i>
%include "datatypes.i"
%include "exceptionsbase.i"

%feature("python:annotations", "c");

// Tell SWIG how to handle our special return type(s) from C++
%template(_string_list) std::vector<std::string>;
%template(_result_list) std::vector<Result>;

%include "snmpbulkget.i"
%include "snmpbulkwalk.i"
%include "snmpget.i"
%include "snmpgetnext.i"
%include "snmpset.i"
%include "snmptrap.i"
%include "snmpwalk.i"