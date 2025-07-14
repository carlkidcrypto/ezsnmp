%module datatypes
%feature("autodoc", "0");

// Directly define the missing conversion macros for the C++ compiler.
// This ensures that any function returning a plain uint32_t or uint64_t
// can be correctly converted to a Python integer object.
%header %{
#define SWIG_From_uint32_t(val) PyLong_FromUnsignedLong(val)
#define SWIG_From_uint64_t(val) PyLong_FromUnsignedLongLong(val)
#define SWIG_From_double(val) PyFloat_FromDouble(val)
#define SWIG_From_int(val) PyLong_FromLong(val)
%}

%include <std_string.i>
%include <std_vector.i>
%include <typemaps.i>

%{
#include <optional>
#include <variant>
#include <string>
#include <vector>
#include <type_traits>
#include "datatypes.h"

// Forward-declare the SWIG helper function for std::string conversion.
// This resolves the compilation order issue.
SWIGINTERN PyObject* SWIG_From_std_string(const std::string& s);

// A visitor struct to convert a variant type to a PyObject*.
// This is a C++11 compatible alternative to a generic lambda.
struct variant_to_pyobject_visitor {
    using result_type = PyObject*;

    result_type operator()(int arg) const {
        return SWIG_From_int(arg);
    }
    result_type operator()(uint32_t arg) const {
        return SWIG_From_uint32_t(arg);
    }
    result_type operator()(uint64_t arg) const {
        return SWIG_From_uint64_t(arg);
    }
    result_type operator()(double arg) const {
        return SWIG_From_double(arg);
    }
    result_type operator()(const std::string& arg) const {
        return SWIG_From_std_string(arg);
    }
    result_type operator()(const std::vector<unsigned char>& arg) const {
        return PyBytes_FromStringAndSize(reinterpret_cast<const char*>(arg.data()), arg.size());
    }
};
%}

// ---- START: ROBUST VARIANT SUPPORT ----
// Provide a simplified declaration for std::variant for SWIG's parser.
template<typename... Ts> class std::variant {};

// This is the core logic for converting a C++ variant to a Python object.
%define VARIANT_OUT_LOGIC(INPUT)
  // Use std::visit with the dedicated visitor struct for broad compiler compatibility.
  $result = std::visit(variant_to_pyobject_visitor{}, INPUT);
%enddef

// Define the full variant type for convenience and clarity.
// Typemap for returning a variant by VALUE or by CONST REFERENCE.
%typemap(out) std::variant<int, uint32_t, uint64_t, double, std::string, std::vector<unsigned char>>,
              const std::variant<int, uint32_t, uint64_t, double, std::string, std::vector<unsigned char>>& {
  VARIANT_OUT_LOGIC($1)
}

// Typemap for returning a variant by POINTER.
%typemap(out) std::variant<int, uint32_t, uint64_t, double, std::string, std::vector<unsigned char>>* {
  if (!$1) {
    $result = Py_None;
    Py_INCREF(Py_None);
  } else {
    // Note the dereference of the pointer: *$1
    VARIANT_OUT_LOGIC(*$1)
  }
}

// Tell SWIG to generate the wrapper for our specific variant instantiation.
%template(ConvertedValue) std::variant<int, uint32_t, uint64_t, double, std::string, std::vector<unsigned char>>;

// ---- END: ROBUST VARIANT SUPPORT ----

// Include the header file
%include "../include/datatypes.h"