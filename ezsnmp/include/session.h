#ifndef SESSION_H
#define SESSION_H

#include <string>
#include <map>

// Take all the Session class inputs and map them to:
// OPTIONS:
//   -v 1|2c|3             specifies SNMP version to use
// SNMP Version 1 or 2c specific
//   -c COMMUNITY          set the community string
// SNMP Version 3 specific
//   -a PROTOCOL           set authentication protocol (MD5|SHA|SHA-224|SHA-256|SHA-384|SHA-512)
//   -A PASSPHRASE         set authentication protocol pass phrase
//   -e ENGINE-ID          set security engine ID (e.g. 800000020109840301)
//   -E ENGINE-ID          set context engine ID (e.g. 800000020109840301)
//   -l LEVEL              set security level (noAuthNoPriv|authNoPriv|authPriv)
//   -n CONTEXT            set context name (e.g. bridge1)
//   -u USER-NAME          set security name (e.g. bert)
//   -x PROTOCOL           set privacy protocol (DES|AES)
//   -X PASSPHRASE         set privacy protocol pass phrase
//   -Z BOOTS,TIME         set destination engine boots/time
// General communication options
//   -r RETRIES            set the number of retries
//   -t TIMEOUT            set the request timeout (in seconds)
std::map<std::string, std::string> cml_param_lookup = {
    {"version", "-v"},
    {"community", "-c"},
    {"auth_protocol", "-a"},
    {"auth_passphrase", "-A"},
    {"security_engine_id", "-e"},
    {"context_engine_id", "-E"},
    {"security_level", "-l"},
    {"context", "-n"},
    {"security_name", "-u"},
    {"privacy_protocol", "-x"},
    {"privacy_passphrase", "-X"},
    {"boots_time", "-Z"},
    {"retires", "-r"},
    {"timeout", "-t"}};

class Session
{
private:
   int m_argc;
   char *m_argv[];

public:
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
           std::string security_name,
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