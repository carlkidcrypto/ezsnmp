%module netsnmp
%feature("autodoc", "0");
%include "stl.i"
%template(_string_list) std::vector< std::string >;
%include "snmpbulkget.i"
%include "snmpbulkwalk.i"
%include "snmpget.i"
%include "snmpwalk.i"
%include "snmpset.i"