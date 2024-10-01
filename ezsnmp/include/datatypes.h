#ifndef DATATYPES_H
#define DATATYPES_H

#include <string>

struct Result
{
    std::string oid;
    std::string type;
    std::string value;

    std::string to_string() const
    {
        return "oid: " + oid + ", type: " + type + ", value: " + value;
    }
};

#endif // DATATYPES_H