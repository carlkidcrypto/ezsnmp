#ifndef SESSION_H
#define SESSION_H

#include <string>

class Session
{
private:
   int m_argc;
   char **m_argv;

public:
   // Defaults are defined in swig interface file. See `interface/session.i`
   Session(std::string hostname,
           std::string port_number,
           std::string version,
           std::string community,
           std::string auth_protocol,
           std::string auth_passphrase,
           std::string security_engine_id,
           std::string context_engine_id,
           std::string security_level,
           std::string context,
           std::string security_username,
           std::string privacy_protocol,
           std::string privacy_passphrase,
           std::string boots_time,
           std::string retires,
           std::string timeout);
   ~Session();

   std::vector<std::string> walk();
   std::vector<std::string> bulk_walk();
   std::vector<std::string> get();
   std::vector<std::string> bulk_get();
};

#endif // SESSION_H