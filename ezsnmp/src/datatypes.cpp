#include "datatypes.h"

std::string Result::to_string() const
{
    return "oid: " + this->oid + ", type: " + this->type + ", value: " + this->value;
}