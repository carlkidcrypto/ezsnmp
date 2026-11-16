%module netsnmp
%include <argcargv.i>
%include <stl.i>
%include "exceptionsbase.i"

%{
#include "snmpusm.h"
%}

// Now list ANSI C/C++ declarations
std::vector<std::string> snmpusm(std::vector<std::string> const &args,
                                 std::string const &init_app_name);
