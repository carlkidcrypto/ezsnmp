%module ezsnmp_swig 
%feature("autodoc", "0");
%include "snmpbulkget.i"
%include "snmpbulkwalk.i"
%include "snmpget.i"
%include "snmpwalk.i"
%template(_string_list) std::vector< std::string >;