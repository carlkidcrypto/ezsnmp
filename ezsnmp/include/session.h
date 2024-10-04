#ifndef SESSION_H
#define SESSION_H

#include <string>
#include <vector>

#include "datatypes.h"

class Session {
  private:
   std::vector<std::string> m_args;
   std::string m_hostname;
   std::string m_port_number;
   std::string m_version;
   std::string m_community;
   std::string m_auth_protocol;
   std::string m_auth_passphrase;
   std::string m_security_engine_id;
   std::string m_context_engine_id;
   std::string m_security_level;
   std::string m_context;
   std::string m_security_username;
   std::string m_privacy_protocol;
   std::string m_privacy_passphrase;
   std::string m_boots_time;
   std::string m_retires;
   std::string m_timeout;

  public:
   Session(std::string hostname = "localhost", std::string port_number = "",
           std::string version = "3", std::string community = "public",
           std::string auth_protocol = "", std::string auth_passphrase = "",
           std::string security_engine_id = "", std::string context_engine_id = "",
           std::string security_level = "", std::string context = "",
           std::string security_username = "", std::string privacy_protocol = "",
           std::string privacy_passphrase = "", std::string boots_time = "",
           std::string retires = "3", std::string timeout = "1");
   ~Session();

   std::vector<Result> walk(std::string mib = "");
   std::vector<std::string> bulk_walk(std::vector<std::string> const& mibs);
   std::vector<std::string> get(std::string mib = "");
   std::vector<std::string> bulk_get(std::vector<std::string> const& mibs);

   // Const getters
   std::vector<std::string> const& args() const;
   std::string const& hostname() const;
   std::string const& port_number() const;
   std::string const& version() const;
   std::string const& community() const;
   std::string const& auth_protocol() const;
   std::string const& auth_passphrase() const;
   std::string const& security_engine_id() const;
   std::string const& context_engine_id() const;
   std::string const& security_level() const;
   std::string const& context() const;
   std::string const& security_username() const;
   std::string const& privacy_protocol() const;
   std::string const& privacy_passphrase() const;
   std::string const& boots_time() const;
   std::string const& retires() const;
   std::string const& timeout() const;
};

#endif // SESSION_H