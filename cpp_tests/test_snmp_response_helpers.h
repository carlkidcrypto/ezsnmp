#pragma once

#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>

namespace ezsnmp_test {

template <typename>
struct first_argument;

template <typename Result, typename First, typename... Rest>
struct first_argument<Result (*)(First, Rest...)> {
   using type = First;
};

using session_handle =
    typename first_argument<decltype(&snmp_sess_synch_response)>::type;
using error_session_handle =
    typename first_argument<decltype(&snmp_sess_error)>::type;

}

inline netsnmp_pdu *make_snmp_generr_response() {
   netsnmp_pdu *response = snmp_pdu_create(SNMP_MSG_RESPONSE);
   response->errstat = SNMP_ERR_GENERR;
   response->errindex = 1;

   oid name[] = {1, 3, 6, 1, 2, 1, 1, 1, 0};
   long value = 1;
   snmp_varlist_add_variable(&response->variables, name, OID_LENGTH(name), ASN_INTEGER,
                             reinterpret_cast<u_char *>(&value), sizeof(value));

   return response;
}
