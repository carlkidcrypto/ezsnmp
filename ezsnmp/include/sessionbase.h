#ifndef SESSIONBASE_H
#define SESSIONBASE_H

#include <string>
#include <vector>

#include "datatypes.h"

class SessionBase {
  private:
   std::vector<std::string> m_args;
   std::string m_hostname = "";
   std::string m_port_number = "";
   std::string m_version = "";
   std::string m_community = "";
   std::string m_auth_protocol = "";
   std::string m_auth_passphrase = "";
   std::string m_security_engine_id = "";
   std::string m_context_engine_id = "";
   std::string m_security_level = "";
   std::string m_context = "";
   std::string m_security_username = "";
   std::string m_privacy_protocol = "";
   std::string m_privacy_passphrase = "";
   std::string m_boots_time = "";
   std::string m_retries = "";
   std::string m_timeout = "";
   void populate_args();
   void check_and_clear_v3_user();

  public:
   SessionBase(std::string hostname = "localhost",
               std::string port_number = "",
               std::string version = "3",
               std::string community = "public",
               std::string auth_protocol = "",
               std::string auth_passphrase = "",
               std::string security_engine_id = "",
               std::string context_engine_id = "",
               std::string security_level = "",
               std::string context = "",
               std::string security_username = "",
               std::string privacy_protocol = "",
               std::string privacy_passphrase = "",
               std::string boots_time = "",
               std::string retries = "3",
               std::string timeout = "1");
   ~SessionBase();

   // walks
   std::vector<Result> walk(std::string mib = "");
   std::vector<Result> bulk_walk(std::vector<std::string> const& mibs);

   // gets
   std::vector<Result> get(std::string mib = "");
   std::vector<Result> get(std::vector<std::string> const& mibs);
   std::vector<Result> get_next(std::vector<std::string> const& mibs);
   std::vector<Result> bulk_get(std::vector<std::string> const& mibs);

   // sets
   std::vector<Result> set(std::vector<std::string> const& mibs);

   // Const getters
   std::vector<std::string> const& _get_args() const;
   std::string const& _get_hostname() const;
   std::string const& _get_port_number() const;
   std::string const& _get_version() const;
   std::string const& _get_community() const;
   std::string const& _get_auth_protocol() const;
   std::string const& _get_auth_passphrase() const;
   std::string const& _get_security_engine_id() const;
   std::string const& _get_context_engine_id() const;
   std::string const& _get_security_level() const;
   std::string const& _get_context() const;
   std::string const& _get_security_username() const;
   std::string const& _get_privacy_protocol() const;
   std::string const& _get_privacy_passphrase() const;
   std::string const& _get_boots_time() const;
   std::string const& _get_retries() const;
   std::string const& _get_timeout() const;

   // Setters
   void _set_hostname(std::string const& hostname);
   void _set_port_number(std::string const& port_number);
   void _set_version(std::string const& version);
   void _set_community(std::string const& community);
   void _set_auth_protocol(std::string const& auth_protocol);
   void _set_auth_passphrase(std::string const& auth_passphrase);
   void _set_security_engine_id(std::string const& security_engine_id);
   void _set_context_engine_id(std::string const& context_engine_id);
   void _set_security_level(std::string const& security_level);
   void _set_context(std::string const& context);
   void _set_security_username(std::string const& security_username);
   void _set_privacy_protocol(std::string const& privacy_protocol);
   void _set_privacy_passphrase(std::string const& privacy_passphrase);
   void _set_boots_time(std::string const& boots_time);
   void _set_retries(std::string const& retries);
   void _set_timeout(std::string const& timeout);
};

#endif // SESSIONBASE_H