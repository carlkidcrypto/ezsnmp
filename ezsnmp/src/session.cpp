#include "session.h"

/******************************************************************************
 * The class contructor. This is a wrapper around the lower level c++ calls.
 * This allows for reuse of given parameters for multiple calls to functions
 * like: snmpwalk, snmpget, etc...
 *
 * @param [in] hostname = "localhost",
 * @param [in] port_number = "",
 * @param [in] version = "3",
 * @param [in] community = "public",
 * @param [in] auth_protocol = "",
 * @param [in]                 auth_passphrase = "",
 * @param [in]                 security_engine_id = "",
 * @param [in]                 context_engine_id = "",
 * @param [in]                 security_level = "",
 * @param [in]                 context = "",
 * @param [in]                 security_name = "",
 * @param [in]                 privacy_protocol = "",
 * @param [in]                 privacy_passphrase = "",
 * @param [in]                 boots_time = "",
 * @param [in]                 retires = "3",
 * @param [in]                 timeout = "1"
 ******************************************************************************/
Session::Session(std::string hostname = "localhost",
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
                 std::string timeout = "1")
{
}

Session::~Session()
{
}
