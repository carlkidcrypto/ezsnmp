#ifndef DATATYPES_H
#define DATATYPES_H

#include <string>

struct Result {
   std::string oid = "";
   std::string index = "";
   std::string type = "";
   std::string value = "";

   std::string to_string() const;
};

#endif // DATATYPES_H