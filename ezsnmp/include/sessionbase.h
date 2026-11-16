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
   std::vector<std::string> m_args; ///< Vector to store SNMP command arguments.
   std::string m_hostname = "";     ///< Hostname or IP address of the SNMP agent [AGENT].
   std::string m_port_number = "";  ///< Port number for the SNMP agent.
   std::string m_version = "";      ///< SNMP version (1|2c|3).
   std::string m_community = "";    ///< Community string (COMMUNITY).
   std::string m_auth_protocol =
       ""; ///< Authentication protocol (MD5|SHA|SHA-224|SHA-256|SHA-384|SHA-512).
   std::string m_auth_passphrase = ""; ///< Authentication protocol pass phrase (PASSPHRASE).
   std::string m_security_engine_id =
       ""; ///< Security engine ID (ENGINE-ID e.g. 800000020109840301).
   std::string m_context_engine_id = ""; ///< Context engine ID (ENGINE-ID e.g. 800000020109840301).
   std::string m_security_level = "";    ///< Security level (noAuthNoPriv|authNoPriv|authPriv).
   std::string m_context = "";           ///< Context name (CONTEXT e.g. bridge1).
   std::string m_security_username = ""; ///< Security name (USER-NAME e.g. bert).
   std::string m_privacy_protocol = "";  ///< Privacy protocol (DES|AES|AES-192|AES-256).
   std::string m_privacy_passphrase = "";  ///< Privacy protocol pass phrase (PASSPHRASE).
   std::string m_boots_time = "";          ///< Destination engine boots/time (BOOTS,TIME).
   std::string m_retries = "";             ///< Number of retries (RETRIES).
   std::string m_timeout = "";             ///< Request timeout in seconds (TIMEOUT).
   std::string m_load_mibs = "";           ///< Load given list of MIBs (MIB[:...]).
   std::string m_mib_directories = "";     ///< Directories to search for MIBs (DIR[:...]).
   bool m_print_enums_numerically = false; ///< Print enums numerically (-O e).
   bool m_print_full_oids = false;         ///< Print full OIDs on output (-O f).
   bool m_print_oids_numerically = false;  ///< Print OIDs numerically (-O n).
   bool m_print_timeticks_numerically =
       false; ///< Print timeticks unparsed as numeric integers (-O t).
   bool m_print_hex_strings =
       false; ///< Print OCTET STRINGs as hex strings when appropriate (-O x).
   std::string m_set_max_repeaters_to_num = ""; ///< Set max-repeaters to <NUM> (-C r<NUM>).
   bool m_print_oid_suffix_only =
       false; ///< Print OIDs using only the last symbolic element (-O s).
   bool m_print_oid_module_name = false;  ///< Print OIDs with module name (-O S).
   bool m_print_oid_ucd_style = false;    ///< Print OIDs using UCD-style prefix suppression (-O u).
   bool m_print_ascii_strings = false;    ///< Print OCTET STRINGs as ASCII strings (-O a).
   bool m_print_leading_zero_hex = false; ///< Print leading 0 on hex values <= 'f' (-O 0).
   bool m_print_hex_text = false;         ///< Print ASCII text along with hex strings (-O T).
   bool m_dont_breakdown_oids = false;    ///< Do not break down OID indexes (-O b).
   bool m_escape_quotes_in_indexes = false; ///< Shell-escape quote marks in OIDs (-O E).
   bool m_extended_index_format = false;    ///< Print extended index format [x1][x2] (-O X).
   bool m_dont_print_units = false;         ///< Do not print UNITS suffix (-O U).
   std::string m_output_precision =
       ""; ///< Printf format string for output precision (-O p <PRECISION>).
   bool m_regex_oid_matching = false;   ///< Use regex matching for OID labels (-I b).
   bool m_ignore_display_hints = false; ///< Do not apply DISPLAY-HINT (-I h).
   bool m_dont_check_range = false;     ///< Do not check values for ranges on send (-I r).
   bool m_random_access_oid = false;    ///< Random access to OID labels (-I R).
   bool m_read_ucd_style_oid = false;   ///< Require top-level OIDs to be prefixed with '.' (-I u).
   std::string m_oid_suffix = "";       ///< Append suffix to OIDs (-I s <SUFFIX>).
   std::string m_oid_prefix = "";       ///< Prepend prefix to OIDs (-I S <PREFIX>).
   bool m_mib_allow_underline = false;  ///< Allow underline characters in MIB labels (-P u).
   bool m_mib_comment_to_eol = false;   ///< Treat '--' as comment to end of line (-P c).
   bool m_mib_replace_with_latest = false; ///< Replace objects from latest MIB module (-P R).
   std::string m_non_repeaters =
       ""; ///< Set non-repeaters to <NUM> (-C n<NUM>). Only applies to GETBULK PDUs.
   bool m_walk_dont_check_lexicographic =
       false;                              ///< Do not check if returned OIDs are increasing (-C c).
   bool m_walk_include_requested = false;  ///< Include requested OID in walk output (-C i).
   bool m_walk_dont_get_requested = false; ///< Do not fall back to GET in walk (-C I).
   std::string m_walk_end_oid = "";        ///< Stop walk at specified OID (-C E <OID>).
   bool m_dont_fix_pdus = false;           ///< Do not fix PDUs on errors (-C f).

   std::string
       m_init_name; ///< Application name for net-snmp initialization (shared by all operations).

   enum class SnmpOperation { All, Get, GetNext, Walk, BulkGet, BulkWalk, Set };

   /**
    * @brief Populates the m_args vector with SNMP command arguments.
    *
    * This private method constructs the command-line arguments for the SNMP
    * command based on the session parameters.
    *
    * @param op The SNMP operation being invoked, used to scope -C application flags.
    */
   void populate_args(SnmpOperation op = SnmpOperation::All);

   /**
    * @brief Clears the cached SNMPv3 user for the current session parameters.
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
    * @param load_mibs Load given list of MIBs (default: "").
    * @param mib_directories Directories to search for MIBs (default: "").
    * @param print_enums_numerically Print enums numerically (default: false).
    * @param print_full_oids Print full OIDs on output (default: false).
    * @param print_oids_numerically Print OIDs numerically (default: false).
    * @param print_timeticks_numerically Print timeticks as numeric integers (default: false).
    * @param print_hex_strings Print OCTET STRING values in hex format when supported (default:
    * false).
    * @param set_max_repeaters_to_num Set max-repeaters to <NUM> (default: ""). Only applies to
    * GETBULK PDUs.
    * @param print_oid_suffix_only Print OIDs using only the last symbolic element (-O s) (default:
    * false).
    * @param print_oid_module_name Print OIDs with module name (-O S) (default: false).
    * @param print_oid_ucd_style Print OIDs using UCD-style prefix suppression (-O u) (default:
    * false).
    * @param print_ascii_strings Print OCTET STRINGs as ASCII strings (-O a) (default: false).
    * @param print_leading_zero_hex Print leading 0 on hex values <= 'f' (-O 0) (default: false).
    * @param print_hex_text Print ASCII text along with hex strings (-O T) (default: false).
    * @param dont_breakdown_oids Do not break down OID indexes (-O b) (default: false).
    * @param escape_quotes_in_indexes Shell-escape quote marks in OIDs (-O E) (default: false).
    * @param extended_index_format Print extended index format [x1][x2] (-O X) (default: false).
    * @param dont_print_units Do not print UNITS suffix (-O U) (default: false).
    * @param output_precision Printf format string for output precision (-O p) (default: "").
    * @param regex_oid_matching Use regex matching for OID labels (-I b) (default: false).
    * @param ignore_display_hints Do not apply DISPLAY-HINT (-I h) (default: false).
    * @param dont_check_range Do not check values for ranges on send (-I r) (default: false).
    * @param random_access_oid Random access to OID labels (-I R) (default: false).
    * @param read_ucd_style_oid Require top-level OIDs to be prefixed with '.' (-I u) (default:
    * false).
    * @param oid_suffix Append suffix to OIDs (-I s) (default: "").
    * @param oid_prefix Prepend prefix to OIDs (-I S) (default: "").
    * @param mib_allow_underline Allow underline characters in MIB labels (-P u) (default: false).
    * @param mib_comment_to_eol Treat '--' as comment to end of line (-P c) (default: false).
    * @param mib_replace_with_latest Replace objects from latest MIB module (-P R) (default: false).
    * @param non_repeaters Set non-repeaters to <NUM> (-C n<NUM>) (default: ""). Only applies to
    * GETBULK PDUs.
    * @param walk_dont_check_lexicographic Do not check if returned OIDs are increasing (-C c)
    * (default: false).
    * @param walk_include_requested Include requested OID in walk output (-C i) (default: false).
    * @param walk_dont_get_requested Do not fall back to GET in walk (-C I) (default: false).
    * @param walk_end_oid Stop walk at specified OID (-C E) (default: "").
    * @param dont_fix_pdus Do not fix PDUs on errors (-C f) (default: false).
    */
   SessionBase(std::string const& hostname = "localhost",
               std::string const& port_number = "",
               std::string const& version = "3",
               std::string const& community = "public",
               std::string const& auth_protocol = "",
               std::string const& auth_passphrase = "",
               std::string const& security_engine_id = "",
               std::string const& context_engine_id = "",
               std::string const& security_level = "",
               std::string const& context = "",
               std::string const& security_username = "",
               std::string const& privacy_protocol = "",
               std::string const& privacy_passphrase = "",
               std::string const& boots_time = "",
               std::string const& retries = "3",
               std::string const& timeout = "1",
               std::string const& load_mibs = "",
               std::string const& mib_directories = "",
               bool print_enums_numerically = false,
               bool print_full_oids = false,
               bool print_oids_numerically = false,
               bool print_timeticks_numerically = false,
               bool print_hex_strings = false,
               std::string const& set_max_repeaters_to_num = "",
               bool print_oid_suffix_only = false,
               bool print_oid_module_name = false,
               bool print_oid_ucd_style = false,
               bool print_ascii_strings = false,
               bool print_leading_zero_hex = false,
               bool print_hex_text = false,
               bool dont_breakdown_oids = false,
               bool escape_quotes_in_indexes = false,
               bool extended_index_format = false,
               bool dont_print_units = false,
               std::string const& output_precision = "",
               bool regex_oid_matching = false,
               bool ignore_display_hints = false,
               bool dont_check_range = false,
               bool random_access_oid = false,
               bool read_ucd_style_oid = false,
               std::string const& oid_suffix = "",
               std::string const& oid_prefix = "",
               bool mib_allow_underline = false,
               bool mib_comment_to_eol = false,
               bool mib_replace_with_latest = false,
               std::string const& non_repeaters = "",
               bool walk_dont_check_lexicographic = false,
               bool walk_include_requested = false,
               bool walk_dont_get_requested = false,
               std::string const& walk_end_oid = "",
               bool dont_fix_pdus = false);

   /**
    * @brief Destructor for SessionBase.
    */
   ~SessionBase();

   /**
    * @brief Closes the SNMP session and releases resources via the snmp snmp_shutdown function.
    * It use the initialization name to identify the session to close.
    * A unique initialization name is generated for each net-snmp function to avoid conflicts.
    * i.e bulkwalk, bulkget, get, getnext, set, walk...
    */
   void _close();

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
    * @brief Performs an SNMP GET NEXT operation.
    *
    * Retrieves the value of the next lexicographically greater OID.
    *
    * @param mib The OID to retrieve the next value for (default: "").
    * @return A vector of Result objects containing the retrieved data.
    */
   std::vector<Result> get_next(std::string const& mib = "");

   /**
    * @brief Performs an SNMP BULK GET operation.
    *
    * Retrieves the values of management information objects using BULK GET.
    *
    * @param mib The OID to retrieve (default: "").
    * @return A vector of Result objects containing the retrieved data.
    */
   std::vector<Result> bulk_get(std::string const& mib = "");

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

   /**
    * @brief Returns the list of MIBs to load.
    *
    * @return A constant reference to the MIB list string.
    */
   std::string const& _get_load_mibs() const;

   /**
    * @brief Returns the directories to search for MIBs.
    *
    * @return A constant reference to the MIB directories string.
    */
   std::string const& _get_mib_directories() const;

   /**
    * @brief Returns whether enums are printed numerically.
    *
    * @return True if enums are printed numerically, false otherwise.
    */
   bool _get_print_enums_numerically() const;

   /**
    * @brief Returns whether full OIDs are printed.
    *
    * @return True if full OIDs are printed, false otherwise.
    */
   bool _get_print_full_oids() const;

   /**
    * @brief Returns whether OIDs are printed numerically.
    *
    * @return True if OIDs are printed numerically, false otherwise.
    */
   bool _get_print_oids_numerically() const;

   /**
    * @brief Returns whether timeticks are printed numerically.
    *
    * @return True if timeticks are printed numerically, false otherwise.
    */
   bool _get_print_timeticks_numerically() const;

   /**
    * @brief Returns whether OCTET STRING values are printed as hex strings.
    *
    * @return True if OCTET STRING values are printed as hex strings, false otherwise.
    */
   bool _get_print_hex_strings() const;

   /**
    * @brief Returns the configured max-repeaters value as a string.
    *
    * @return A constant reference to the max-repeaters string.
    */
   std::string const& _get_set_max_repeaters_to_num() const;

   /**
    * @brief Returns whether OIDs are printed using only the last symbolic element.
    *
    * @return True if OID suffix only is printed, false otherwise.
    */
   bool _get_print_oid_suffix_only() const;

   /**
    * @brief Returns whether OIDs are printed with their module name.
    *
    * @return True if OID module name is printed, false otherwise.
    */
   bool _get_print_oid_module_name() const;

   /**
    * @brief Returns whether OIDs are printed using UCD-style prefix suppression.
    *
    * @return True if UCD-style OIDs are printed, false otherwise.
    */
   bool _get_print_oid_ucd_style() const;

   /**
    * @brief Returns whether OCTET STRING values are printed as ASCII strings.
    *
    * @return True if ASCII strings are printed, false otherwise.
    */
   bool _get_print_ascii_strings() const;

   /**
    * @brief Returns whether a leading 0 is printed on hex values <= 'f'.
    *
    * @return True if leading zero hex is enabled, false otherwise.
    */
   bool _get_print_leading_zero_hex() const;

   /**
    * @brief Returns whether ASCII text is printed along with hex strings.
    *
    * @return True if hex text is printed, false otherwise.
    */
   bool _get_print_hex_text() const;

   /**
    * @brief Returns whether OID index breakdown is disabled.
    *
    * @return True if OID breakdown is disabled, false otherwise.
    */
   bool _get_dont_breakdown_oids() const;

   /**
    * @brief Returns whether quote marks in OID indexes are shell-escaped.
    *
    * @return True if quotes in indexes are escaped, false otherwise.
    */
   bool _get_escape_quotes_in_indexes() const;

   /**
    * @brief Returns whether extended index format [x1][x2] is enabled.
    *
    * @return True if extended index format is enabled, false otherwise.
    */
   bool _get_extended_index_format() const;

   /**
    * @brief Returns whether UNITS suffix printing is disabled.
    *
    * @return True if UNITS suffix printing is disabled, false otherwise.
    */
   bool _get_dont_print_units() const;

   /**
    * @brief Returns the output precision format string.
    *
    * @return A constant reference to the output precision string.
    */
   std::string const& _get_output_precision() const;

   /**
    * @brief Returns whether regex matching for OID labels is enabled.
    *
    * @return True if regex OID matching is enabled, false otherwise.
    */
   bool _get_regex_oid_matching() const;

   /**
    * @brief Returns whether DISPLAY-HINT is ignored on input.
    *
    * @return True if display hints are ignored, false otherwise.
    */
   bool _get_ignore_display_hints() const;

   /**
    * @brief Returns whether range checking is disabled on send.
    *
    * @return True if range checking is disabled, false otherwise.
    */
   bool _get_dont_check_range() const;

   /**
    * @brief Returns whether random access to OID labels is enabled.
    *
    * @return True if random access OID is enabled, false otherwise.
    */
   bool _get_random_access_oid() const;

   /**
    * @brief Returns whether top-level OIDs require a leading dot on input.
    *
    * @return True if UCD-style input OIDs are required, false otherwise.
    */
   bool _get_read_ucd_style_oid() const;

   /**
    * @brief Returns the OID suffix appended to input OIDs.
    *
    * @return A constant reference to the OID suffix string.
    */
   std::string const& _get_oid_suffix() const;

   /**
    * @brief Returns the OID prefix prepended to input OIDs.
    *
    * @return A constant reference to the OID prefix string.
    */
   std::string const& _get_oid_prefix() const;

   /**
    * @brief Returns whether underline characters are allowed in MIB labels.
    *
    * @return True if underlines are allowed in MIB labels, false otherwise.
    */
   bool _get_mib_allow_underline() const;

   /**
    * @brief Returns whether '--' is treated as a comment to end of line.
    *
    * @return True if MIB comment to EOL is enabled, false otherwise.
    */
   bool _get_mib_comment_to_eol() const;

   /**
    * @brief Returns whether MIB objects are replaced from the latest module.
    *
    * @return True if MIB replace with latest is enabled, false otherwise.
    */
   bool _get_mib_replace_with_latest() const;

   /**
    * @brief Returns the configured non-repeaters value as a string.
    *
    * @return A constant reference to the non-repeaters string.
    */
   std::string const& _get_non_repeaters() const;

   /**
    * @brief Returns whether lexicographic OID ordering check is disabled in walk.
    *
    * @return True if lexicographic check is disabled, false otherwise.
    */
   bool _get_walk_dont_check_lexicographic() const;

   /**
    * @brief Returns whether the requested OID is included in walk output.
    *
    * @return True if the requested OID is included, false otherwise.
    */
   bool _get_walk_include_requested() const;

   /**
    * @brief Returns whether GET fallback is disabled when GETNEXT returns nothing in walk.
    *
    * @return True if GET fallback is disabled, false otherwise.
    */
   bool _get_walk_dont_get_requested() const;

   /**
    * @brief Returns the end OID for walk operations.
    *
    * @return A constant reference to the walk end OID string.
    */
   std::string const& _get_walk_end_oid() const;

   /**
    * @brief Returns whether PDU fixing on errors is disabled for get/get_next.
    *
    * @return True if PDU fixing is disabled, false otherwise.
    */
   bool _get_dont_fix_pdus() const;

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

   /**
    * @brief Sets the list of MIBs to load.
    *
    * @param load_mibs The new list of MIBs to load.
    */
   void _set_load_mibs(std::string const& load_mibs);

   /**
    * @brief Sets the directories to search for MIBs.
    *
    * @param mib_directories The new directories to search for MIBs.
    */
   void _set_mib_directories(std::string const& mib_directories);

   /**
    * @brief Sets whether to print enums numerically.
    *
    * @param print_enums_numerically The new value for printing enums numerically.
    */
   void _set_print_enums_numerically(bool print_enums_numerically);

   /**
    * @brief Sets whether to print full OIDs on output.
    *
    * @param print_full_oids The new value for printing full OIDs.
    */
   void _set_print_full_oids(bool print_full_oids);

   /**
    * @brief Sets whether to print OIDs numerically.
    *
    * @param print_oids_numerically The new value for printing OIDs numerically.
    */
   void _set_print_oids_numerically(bool print_oids_numerically);

   /**
    * @brief Sets whether to print timeticks as numeric integers.
    *
    * @param print_timeticks_numerically The new value for printing timeticks numerically.
    */
   void _set_print_timeticks_numerically(bool print_timeticks_numerically);

   /**
    * @brief Sets whether to print OCTET STRING values as hex strings.
    *
    * @param print_hex_strings The new value for printing OCTET STRING values as hex strings.
    */
   void _set_print_hex_strings(bool print_hex_strings);

   /**
    * @brief Sets max-repeaters to <NUM>.
    *
    * @param set_max_repeaters_to_num The new value for max-repeaters.
    */
   void _set_max_repeaters_to_num(std::string const& set_max_repeaters_to_num);

   /**
    * @brief Sets whether to print OIDs using only the last symbolic element (-O s).
    *
    * @param print_oid_suffix_only The new value for printing OID suffix only.
    */
   void _set_print_oid_suffix_only(bool print_oid_suffix_only);

   /**
    * @brief Sets whether to print OIDs with their module name (-O S).
    *
    * @param print_oid_module_name The new value for printing OID module name.
    */
   void _set_print_oid_module_name(bool print_oid_module_name);

   /**
    * @brief Sets whether to print OIDs using UCD-style prefix suppression (-O u).
    *
    * @param print_oid_ucd_style The new value for printing UCD-style OIDs.
    */
   void _set_print_oid_ucd_style(bool print_oid_ucd_style);

   /**
    * @brief Sets whether to print OCTET STRING values as ASCII strings (-O a).
    *
    * @param print_ascii_strings The new value for printing ASCII strings.
    */
   void _set_print_ascii_strings(bool print_ascii_strings);

   /**
    * @brief Sets whether to print a leading 0 on hex values <= 'f' (-O 0).
    *
    * @param print_leading_zero_hex The new value for printing leading zero hex.
    */
   void _set_print_leading_zero_hex(bool print_leading_zero_hex);

   /**
    * @brief Sets whether to print ASCII text along with hex strings (-O T).
    *
    * @param print_hex_text The new value for printing hex text.
    */
   void _set_print_hex_text(bool print_hex_text);

   /**
    * @brief Sets whether to disable OID index breakdown (-O b).
    *
    * @param dont_breakdown_oids The new value for disabling OID breakdown.
    */
   void _set_dont_breakdown_oids(bool dont_breakdown_oids);

   /**
    * @brief Sets whether to shell-escape quote marks in OID indexes (-O E).
    *
    * @param escape_quotes_in_indexes The new value for escaping quotes in indexes.
    */
   void _set_escape_quotes_in_indexes(bool escape_quotes_in_indexes);

   /**
    * @brief Sets whether to use extended index format [x1][x2] (-O X).
    *
    * @param extended_index_format The new value for extended index format.
    */
   void _set_extended_index_format(bool extended_index_format);

   /**
    * @brief Sets whether to disable UNITS suffix printing (-O U).
    *
    * @param dont_print_units The new value for disabling UNITS printing.
    */
   void _set_dont_print_units(bool dont_print_units);

   /**
    * @brief Sets the output precision format string (-O p).
    *
    * @param output_precision The new output precision format string.
    */
   void _set_output_precision(std::string const& output_precision);

   /**
    * @brief Sets whether to enable regex matching for OID labels (-I b).
    *
    * @param regex_oid_matching The new value for regex OID matching.
    */
   void _set_regex_oid_matching(bool regex_oid_matching);

   /**
    * @brief Sets whether to ignore DISPLAY-HINT on input (-I h).
    *
    * @param ignore_display_hints The new value for ignoring display hints.
    */
   void _set_ignore_display_hints(bool ignore_display_hints);

   /**
    * @brief Sets whether to disable range checking on send (-I r).
    *
    * @param dont_check_range The new value for disabling range checks.
    */
   void _set_dont_check_range(bool dont_check_range);

   /**
    * @brief Sets whether to enable random access to OID labels (-I R).
    *
    * @param random_access_oid The new value for random access OIDs.
    */
   void _set_random_access_oid(bool random_access_oid);

   /**
    * @brief Sets whether to require top-level OIDs to be prefixed with '.' (-I u).
    *
    * @param read_ucd_style_oid The new value for reading UCD-style OIDs.
    */
   void _set_read_ucd_style_oid(bool read_ucd_style_oid);

   /**
    * @brief Sets the OID suffix appended to input OIDs (-I s).
    *
    * @param oid_suffix The new OID suffix string.
    */
   void _set_oid_suffix(std::string const& oid_suffix);

   /**
    * @brief Sets the OID prefix prepended to input OIDs (-I S).
    *
    * @param oid_prefix The new OID prefix string.
    */
   void _set_oid_prefix(std::string const& oid_prefix);

   /**
    * @brief Sets whether underline characters are allowed in MIB labels (-P u).
    *
    * @param mib_allow_underline The new value for allowing underlines in MIB labels.
    */
   void _set_mib_allow_underline(bool mib_allow_underline);

   /**
    * @brief Sets whether '--' is treated as a comment to end of line (-P c).
    *
    * @param mib_comment_to_eol The new value for MIB comment to EOL.
    */
   void _set_mib_comment_to_eol(bool mib_comment_to_eol);

   /**
    * @brief Sets whether MIB objects are replaced from the latest module (-P R).
    *
    * @param mib_replace_with_latest The new value for MIB replace with latest.
    */
   void _set_mib_replace_with_latest(bool mib_replace_with_latest);

   /**
    * @brief Sets non-repeaters to <NUM> (-C n<NUM>).
    *
    * @param non_repeaters The new value for non-repeaters.
    */
   void _set_non_repeaters(std::string const& non_repeaters);

   /**
    * @brief Sets whether to disable lexicographic OID ordering check in walk (-C c).
    *
    * @param walk_dont_check_lexicographic The new value for disabling lexicographic check.
    */
   void _set_walk_dont_check_lexicographic(bool walk_dont_check_lexicographic);

   /**
    * @brief Sets whether to include the requested OID in walk output (-C i).
    *
    * @param walk_include_requested The new value for including requested OID.
    */
   void _set_walk_include_requested(bool walk_include_requested);

   /**
    * @brief Sets whether to disable GET fallback when GETNEXT returns nothing in walk (-C I).
    *
    * @param walk_dont_get_requested The new value for disabling GET fallback.
    */
   void _set_walk_dont_get_requested(bool walk_dont_get_requested);

   /**
    * @brief Sets the end OID for walk operations (-C E).
    *
    * @param walk_end_oid The new walk end OID string.
    */
   void _set_walk_end_oid(std::string const& walk_end_oid);

   /**
    * @brief Sets whether to disable PDU fixing on errors for get/get_next (-C f).
    *
    * @param dont_fix_pdus The new value for disabling PDU fixing.
    */
   void _set_dont_fix_pdus(bool dont_fix_pdus);
};

#endif // SESSIONBASE_H