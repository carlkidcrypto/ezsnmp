%module datatypesbase
%feature("autodoc", "0");

%include <std_string.i>

%{
#include <optional>
#include "datatypesbase.h"
%}

// Start: https://github.com/nobleo/Fields2Cover/blob/144ed1c6ba5dd0ddac0a72d6f4e11db0598cb040/swig/optional.i#L8-L22
// Provide simplified declarations of various template classes we use for SWIG.
template <typename T>
class std::optional
{
public:
  optional();
  optional(const T& value);
  optional(const optional& other);
  optional& operator=(const optional& other);

  bool has_value() const;

  const T& value() const;
  T& emplace(const T&);
  void reset();
};
// End: https://github.com/nobleo/Fields2Cover/blob/144ed1c6ba5dd0ddac0a72d6f4e11db0598cb040/swig/optional.i#L8-L22

// Start: https://github.com/nobleo/Fields2Cover/blob/144ed1c6ba5dd0ddac0a72d6f4e11db0598cb040/swig/python/optional.i
%define DEFINE_OPTIONAL_SIMPLE(OptT, T)

// Use reference, not pointer, typemaps for member variables of this type.
%naturalvar std::optional< T >;

// Even though this type is not mentioned anywhere, we must still do this to
// tell SWIG to actually export this type.
%template(OptT) std::optional< T >;

// This typemap is used for function arguments and for setting member fields of
// std::optional<> type.
//
// Also note the hack with shadowing $1 below: it is a bit ridiculous, but it
// seems like we don't have any way to reuse the typemap defined for T without
// defining this nested variable with the same name as the original one, but
// with the right type. I.e. this $1 intentionally hides the real $1, of type
// "std::optional<T>*", so that $typemap() code compiles correctly.
%typemap(in) std::optional< T >, const std::optional< T >& (std::optional< T > tmp_ov) %{
  $1 = &tmp_ov;
  if ($input != Py_None)
  {
    T $1;
    $typemap(in, T)
    tmp_ov = $1;
  }
  %}

// For dynamic languages, such as Python, there should be a typecheck typemap
// for each in typemap to allow overloaded functions taking this type to work.
%typemap(typecheck, precedence=SWIG_TYPECHECK_POINTER) std::optional< T >, const std::optional< T >& (std::optional< T > tmp_ov) %{
  if ($input == Py_None)
    $1 = true;
  else {
    $typemap(typecheck, T)
  }
  %}

// This typemap is for functions returning objects of this type.
//
// It again needs to use an ugly trick with shadowing, this time of "result",
// to make the code from $typemap() expansion work correctly.
%typemap(out) std::optional< T > %{
  if ( $1.has_value() )
  {
    std::optional< T >& tmp_ov = $1;
    {
      T result = tmp_ov.value();
      $typemap(out, T)
    }
  }
  else
  {
    $result = Py_None;
    Py_INCREF(Py_None);
  }
  %}

// And this one is for members of this type.
//
// It's basically the same as above, but the type of "$1" is different here.
%typemap(out) std::optional< T >& %{
  if ( $1->has_value() )
  {
    std::optional< T >* tmp_ptr = $1;
    {
      T result = tmp_ptr->value();
      $typemap(out, T)
    }
  }
  else
  {
    $result = Py_None;
    Py_INCREF(Py_None);
  }
  %}


%enddef
// End: https://github.com/nobleo/Fields2Cover/blob/144ed1c6ba5dd0ddac0a72d6f4e11db0598cb040/swig/python/optional.i

%template(optional_int) std::optional<int>;
%template(optional_uint32_t) std::optional<uint32_t>;
%template(optional_uint64_t) std::optional<uint64_t>;
%template(optional_double) std::optional<double>;
%template(optional_std_string) std::optional<std::string>;

// Include the header file
%include "../include/datatypesbase.h"