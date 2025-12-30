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

// Forward-declare the SWIG helper function for std::string conversion
// to resolve potential compilation order issues.
SWIGINTERN PyObject* SWIG_From_std_string(const std::string& s);

// A visitor struct to convert a variant type to a PyObject*.
// This is a C++11/14 compatible alternative to a generic lambda and provides
// a clean way to organize the conversion logic.
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
        // FIX: Check for and remove wrapping quotes from malformed SNMP strings.
        // https://github.com/carlkidcrypto/ezsnmp/issues/355
        if (arg.length() >= 2 && arg.front() == '"' && arg.back() == '"') {
            // Create a new C++ string containing just the inner content.
            std::string cleaned_str = arg.substr(1, arg.length() - 2);
            // Convert the *cleaned* string to a Python object.
            return SWIG_From_std_string(cleaned_str);
        }
        
        // If no wrapping quotes are found, convert the original string as usual.
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
// It uses a series of `if-else if` checks with `std::get_if` as a robust
// alternative to `std::visit`, which is unavailable on older macOS targets.
%define VARIANT_OUT_LOGIC(INPUT)
  // Create an instance of our visitor to handle the type-specific conversions.
  variant_to_pyobject_visitor visitor;

  // Check the type held by the variant and call the appropriate visitor function.
  // std::get_if returns a pointer to the value if the variant holds that type,
  // otherwise it returns nullptr.
  if (auto* val = std::get_if<int>(&(INPUT))) {
    $result = visitor(*val);
  } else if (auto* val = std::get_if<uint32_t>(&(INPUT))) {
    $result = visitor(*val);
  } else if (auto* val = std::get_if<uint64_t>(&(INPUT))) {
    $result = visitor(*val);
  } else if (auto* val = std::get_if<double>(&(INPUT))) {
    $result = visitor(*val);
  } else if (auto* val = std::get_if<std::string>(&(INPUT))) {
    $result = visitor(*val);
  } else if (auto* val = std::get_if<std::vector<unsigned char>>(&(INPUT))) {
    $result = visitor(*val);
  } else {
    // This case should not be reached if the variant is valid.
    // Set a Python exception to indicate a problem.
    SWIG_exception_fail(SWIG_TypeError, "Variant holds an unexpected or unhandled type.");
  }
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

// ---- START: PYTHON SPECIAL METHODS FOR RESULT ----
// Add Python __str__ and __repr__ methods to the Result struct
%extend Result {
    %pythoncode %{
    def __str__(self):
        """Return a user-friendly string representation of the Result object."""
        return self._to_string()

    def __repr__(self):
        """Return a detailed string representation of the Result object."""
        return f"Result({self._to_string()})"

    def to_dict(self):
        """Convert the Result object to a dictionary for logging or JSON serialization.

        :return: A dictionary containing all result fields.
        :rtype: dict
        """
        # Get converted_value as the appropriate Python type
        conv_val = self.converted_value

        return {
            "oid": self.oid,
            "index": self.index,
            "type": self.type,
            "value": self.value,
            "converted_value": conv_val,
        }
    %}
}
// ---- END: PYTHON SPECIAL METHODS FOR RESULT ----