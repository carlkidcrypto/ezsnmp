#include "datatypes.h"

std::string Result::to_string() const
{
    return "oid: " + oid + ", type: " + type + ", value: " + value;
}