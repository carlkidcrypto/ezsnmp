#ifndef SESSIONBASE_H
#define SESSIONBASE_H

#include <string>
#include <vector>

#include "datatypes.h"

/**
 * @brief Base class for managing SNMP sessions.
 *
 * This class provides a base for managing SNMP sessions, including
 * connection parameters, authentication, and basic operations like
 * GET, SET, and WALK.
 */
class SessionBase {
  private:
   std::vector<std::string> m_args;  ///< Vector to store SNMP command arguments.
   std::string m_hostname = "";      ///< Hostname or IP address of the SNMP agent.
   std::string m_port_number = "";   ///< Port number for the SNMP agent.
   std::string m_version = "";       ///< SNMP version ("1", "2c", or "3").
   std::string m_community = "";     ///< Community string for SNMP v1/v2c.
   std::string m_auth_protocol = ""; ///< Authentication protocol for SNMP v3 (e.g., "MD5", "SHA").
   std::string m_auth_passphrase = "";    ///< Authentication passphrase for SNMP v3.
   std::string m_security_engine_id = ""; ///< Security engine ID for SNMP v3.
   std::string m_context_engine_id = "";  ///< Context engine ID for SNMP v3.
   std::string m_security_level =
       ""; ///< Security level for SNMP v3 (e.g., "noAuthNoPriv", "authNoPriv", "authPriv").
   std::string m_context = "";            ///< Context name for SNMP v3.
   std::string m_security_username = "";  ///< Security username for SNMP v3.
   std::string m_privacy_protocol = "";   ///< Privacy protocol for SNMP v3 (e.g., "DES", "AES").
   std::string m_privacy_passphrase = ""; ///< Privacy passphrase for SNMP v3.
   std::string m_boots_time = "";         ///< System boots time for SNMP v3.
   std::string m_retries = "";            ///< Number of retries for SNMP requests.
   std::string m_timeout = "";            ///< Timeout for SNMP requests.

   /**
    * @brief Populates the m_args vector with SNMP command arguments.
    *
    * This private method constructs the command-line arguments for the SNMP
    * command based on the session parameters.
    */
   void populate_args();

   /**
    * @brief Checks and clears SNMP v3 user parameters if not applicable.
    *
    * This private method ensures that SNMP v3 user-related parameters
    * are cleared if the SNMP version is not 3.
    */
   void check_and_clear_v3_user();

  public:
   /**
    * @brief Constructor for SessionBase.
    *
    * Initializes a new SessionBase object with the provided parameters.
    *
    * @param hostname Hostname or IP address of the SNMP agent (default: "localhost").
    * @param port_number Port number for the SNMP agent (default: "").
    * @param version SNMP version ("1", "2c", or "3") (default: "3").
    * @param community Community string for SNMP v1/v2c (default: "public").
    * @param auth_protocol Authentication protocol for SNMP v3 (default: "").
    * @param auth_passphrase Authentication passphrase for SNMP v3 (default: "").
    * @param security_engine_id Security engine ID for SNMP v3 (default: "").
    * @param context_engine_id Context engine ID for SNMP v3 (default: "").
    * @param security_level Security level for SNMP v3 (default: "").
    * @param context Context name for SNMP v3 (default: "").
    * @param security_username Security username for SNMP v3 (default: "").
    * @param privacy_protocol Privacy protocol for SNMP v3 (default: "").
    * @param privacy_passphrase Privacy passphrase for SNMP v3 (default: "").
    * @param boots_time System boots time for SNMP v3 (default: "").
    * @param retries Number of retries for SNMP requests (default: "3").
    * @param timeout Timeout for SNMP requests (default: "1").
    */
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

   /**
    * @brief Destructor for SessionBase.
    */
   ~SessionBase();

   /**
    * @brief Performs an SNMP WALK operation.
    *
    * Retrieves a subtree of management information using SNMP WALK.
    *
    * @param mib The OID (Object Identifier) to start the walk from (default: "").
    * @return A vector of Result objects containing the retrieved data.
    */
   std::vector<Result> walk(std::string const& mib = "");

   /**
    * @brief Performs an SNMP BULK WALK operation.
    *
    * Retrieves a subtree of management information using SNMP BULK WALK.
    *
    * @param mib The OID to start the walk from.
    * @return A vector of Result objects containing the retrieved data.
    */
   std::vector<Result> bulk_walk(std::string const& mib);

   /**
    * @brief Performs an SNMP BULK WALK operation on multiple OIDs.
    *
    * Retrieves subtrees of management information using SNMP BULK WALK for multiple OIDs.
    *
    * @param mibs A vector of OIDs to start the walks from.
    * @return A vector of Result objects containing the retrieved data.
    */
   std::vector<Result> bulk_walk(std::vector<std::string> const& mibs);

   /**
    * @brief Performs an SNMP GET operation.
    *
    * Retrieves the value of a specific management information object.
    *
    * @param mib The OID of the object to retrieve (default: "").
    * @return A vector of Result objects containing the retrieved data.
    */
   std::vector<Result> get(std::string const& mib = "");

   /**
    * @brief Performs an SNMP GET operation on multiple OIDs.
    *
    * Retrieves the values of multiple management information objects.
    *
    * @param mibs A vector of OIDs to retrieve.
    * @return A vector of Result objects containing the retrieved data.
    */
   std::vector<Result> get(std::vector<std::string> const& mibs);

   /**
    * @brief Performs an SNMP GET NEXT operation on multiple OIDs.
    *
    * Retrieves the values of the next lexicographically greater OIDs.
    *
    * @param mibs A vector of OIDs to retrieve the next values for.
    * @return A vector of Result objects containing the retrieved data.
    */
   std::vector<Result> get_next(std::vector<std::string> const& mibs);

   /**
    * @brief Performs an SNMP BULK GET operation on multiple OIDs.
    *
    * Retrieves the values of multiple management information objects using BULK GET.
    *
    * @param mibs A vector of OIDs to retrieve.
    * @return A vector of Result objects containing the retrieved data.
    */
   std::vector<Result> bulk_get(std::vector<std::string> const& mibs);

   /**
    * @brief Performs an SNMP SET operation on multiple OIDs.
    *
    * Sets the values of multiple management information objects.
    *
    * @param mibs A vector of OIDs and their corresponding values to set.
    * @return A vector of Result objects containing the results of the SET operation.
    */
   std::vector<Result> set(std::vector<std::string> const& mibs);

   // Const getters

   /**
    * @brief Returns the SNMP command arguments.
    *
    * @return A constant reference to the vector of SNMP command arguments.
    */
   std::vector<std::string> const& _get_args() const;

   /**
    * @brief Returns the hostname of the SNMP agent.
    *
    * @return A constant reference to the hostname.
    */
   std::string const& _get_hostname() const;

   /**
    * @brief Returns the port number for the SNMP agent.
    *
    * @return A constant reference to the port number.
    */
   std::string const& _get_port_number() const;

   /**
    * @brief Returns the SNMP version.
    *
    * @return A constant reference to the SNMP version.
    */
   std::string const& _get_version() const;

   /**
    * @brief Returns the community string.
    *
    * @return A constant reference to the community string.
    */
   std::string const& _get_community() const;

   /**
    * @brief Returns the authentication protocol.
    *
    * @return A constant reference to the authentication protocol.
    */
   std::string const& _get_auth_protocol() const;

   /**
    * @brief Returns the authentication passphrase.
    *
    * @return A constant reference to the authentication passphrase.
    */
   std::string const& _get_auth_passphrase() const;

   /**
    * @brief Returns the security engine ID.
    *
    * @return A constant reference to the security engine ID.
    */
   std::string const& _get_security_engine_id() const;

   /**
    * @brief Returns the context engine ID.
    *
    * @return A constant reference to the context engine ID.
    */
   std::string const& _get_context_engine_id() const;

   /**
    * @brief Returns the security level.
    *
    * @return A constant reference to the security level.
    */
   std::string const& _get_security_level() const;

   /**
    * @brief Returns the context name.
    *
    * @return A constant reference to the context name.
    */
   std::string const& _get_context() const;

   /**
    * @brief Returns the security username.
    *
    * @return A constant reference to the security username.
    */
   std::string const& _get_security_username() const;

   /**
    * @brief Returns the privacy protocol.
    *
    * @return A constant reference to the privacy protocol.
    */
   std::string const& _get_privacy_protocol() const;

   /**
    * @brief Returns the privacy passphrase.
    *
    * @return A constant reference to the privacy passphrase.
    */
   std::string const& _get_privacy_passphrase() const;

   /**
    * @brief Returns the system boots time.
    *
    * @return A constant reference to the system boots time.
    */
   std::string const& _get_boots_time() const;

   /**
    * @brief Returns the number of retries.
    *
    * @return A constant reference to the number of retries.
    */
   std::string const& _get_retries() const;

   /**
    * @brief Returns the timeout value.
    *
    * @return A constant reference to the timeout value.
    */
   std::string const& _get_timeout() const;

   // Setters

   /**
    * @brief Sets the hostname of the SNMP agent.
    *
    * @param hostname The new hostname to set.
    */
   void _set_hostname(std::string const& hostname);

   /**
    * @brief Sets the port number for the SNMP agent.
    *
    * @param port_number The new port number to set.
    */
   void _set_port_number(std::string const& port_number);

   /**
    * @brief Sets the SNMP version.
    *
    * @param version The new SNMP version to set.
    */
   void _set_version(std::string const& version);

   /**
    * @brief Sets the community string.
    *
    * @param community The new community string to set.
    */
   void _set_community(std::string const& community);

   /**
    * @brief Sets the authentication protocol.
    *
    * @param auth_protocol The new authentication protocol to set.
    */
   void _set_auth_protocol(std::string const& auth_protocol);

   /**
    * @brief Sets the authentication passphrase.
    *
    * @param auth_passphrase The new authentication passphrase to set.
    */
   void _set_auth_passphrase(std::string const& auth_passphrase);

   /**
    * @brief Sets the security engine ID.
    *
    * @param security_engine_id The new security engine ID to set.
    */
   void _set_security_engine_id(std::string const& security_engine_id);

   /**
    * @brief Sets the context engine ID.
    *
    * @param context_engine_id The new context engine ID to set.
    */
   void _set_context_engine_id(std::string const& context_engine_id);

   /**
    * @brief Sets the security level.
    *
    * @param security_level The new security level to set.
    */
   void _set_security_level(std::string const& security_level);

   /**
    * @brief Sets the context name.
    *
    * @param context The new context name to set.
    */
   void _set_context(std::string const& context);

   /**
    * @brief Sets the security username.
    *
    * @param security_username The new security username to set.
    */
   void _set_security_username(std::string const& security_username);

   /**
    * @brief Sets the privacy protocol.
    *
    * @param privacy_protocol The new privacy protocol to set.
    */
   void _set_privacy_protocol(std::string const& privacy_protocol);

   /**
    * @brief Sets the privacy passphrase.
    *
    * @param privacy_passphrase The new privacy passphrase to set.
    */
   void _set_privacy_passphrase(std::string const& privacy_passphrase);

   /**
    * @brief Sets the system boots time.
    *
    * @param boots_time The new system boots time to set.
    */
   void _set_boots_time(std::string const& boots_time);

   /**
    * @brief Sets the number of retries.
    *
    * @param retries The new number of retries to set.
    */
   void _set_retries(std::string const& retries);

   /**
    * @brief Sets the timeout value.
    *
    * @param timeout The new timeout value to set.
    */
   void _set_timeout(std::string const& timeout);
};

#endif // SESSIONBASE_H