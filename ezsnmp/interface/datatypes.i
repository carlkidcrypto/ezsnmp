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
%include <typemaps.i>

%{
#include <optional>
#include <variant>
#include <type_traits>
#include "datatypes.h"
%}

// ---- START: ROBUST VARIANT SUPPORT ----
// Provide a simplified declaration for std::variant
template<typename... Ts> class std::variant {};

// This is the core logic for converting a C++ variant to a Python object.
%define VARIANT_OUT_LOGIC(INPUT)
  // Use std::visit with a generic lambda.
  $result = std::visit([](auto&& arg) -> PyObject* {
    using T = std::decay_t<decltype(arg)>;
    if constexpr (std::is_same_v<T, int>) {
        return SWIG_From_int(arg);
    } else if constexpr (std::is_same_v<T, uint32_t>) {
        return SWIG_From_uint32_t(arg);
    } else if constexpr (std::is_same_v<T, uint64_t>) {
        return SWIG_From_uint64_t(arg);
    } else if constexpr (std::is_same_v<T, double>) {
        return SWIG_From_double(arg);
    } else if constexpr (std::is_same_v<T, std::string>) {
        return SWIG_From_std_string(arg);
    } else if constexpr (std::is_same_v<T, std::vector<unsigned char>>) {
        return PyBytes_FromStringAndSize(reinterpret_cast<const char*>(arg.data()), arg.size());
    }
    // This path should be unreachable for the given variant types
    Py_RETURN_NONE;
  }, INPUT);
%enddef

// Define the full variant type for convenience and clarity
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