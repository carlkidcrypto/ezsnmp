#include <string>

class Session
{
private:
   int m_argc;
   char *m_argv[];

public:
   Session(std::string hostname = "localhost",
           std::string port_number = "",
           std::string version = "3",
           std::string community = "public",
           std::string auth_protocol = "",
           std::string auth_passphrase = "",
           std::string security_engine_id = "",
           std::string context_engine_id = "",
           std::string security_level = "",
           std::string context = "",
           std::string security_name = "",
           std::string privacy_protocol = "",
           std::string privacy_passphrase = "",
           std::string boots_time = "",
           std::string retires = "3",
           std::string timeout = "1");
   ~Session();
};