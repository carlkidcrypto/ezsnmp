%module datatypes
%feature("autodoc", "0");

%include <std_string.i>

%{
#include "datatypes.h"
%}

// Tell SWIG how to map std::variant<int, uint32_t, uint64_t, double, std::string> to Python types
%typemap(out) SwigValueWrapper<std::variant<int, uint32_t, uint64_t, double, std::string>> {
    const std::variant<int, uint32_t, uint64_t, double, std::string>& var = $1;
    if (std::holds_alternative<int>(var)) {
        $result = PyLong_FromLong(static_cast<long>(std::get<int>(var)));
    } else if (std::holds_alternative<uint32_t>(var)) {
        $result = PyLong_FromUnsignedLong(static_cast<unsigned long>(std::get<uint32_t>(var)));
    } else if (std::holds_alternative<uint64_t>(var)) {
        $result = PyLong_FromUnsignedLongLong(static_cast<unsigned long long>(std::get<uint64_t>(var)));
    } else if (std::holds_alternative<double>(var)) {
        $result = PyFloat_FromDouble(std::get<double>(var));
    } else if (std::holds_alternative<std::string>(var)) {
        const std::string* str_ptr = std::get_if<std::string>(&var);
        if (str_ptr) {
            $result = SWIG_From_std_string(*str_ptr);
        } else {
            Py_INCREF(Py_None);
            $result = Py_None;
        }
    } else {
        Py_INCREF(Py_None);
        $result = Py_None;
    }
}

// Include the header file
%include "../include/datatypes.h"