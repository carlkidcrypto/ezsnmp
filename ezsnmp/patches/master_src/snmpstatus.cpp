/* straight copy from https://github.com/net-snmp/net-snmp/tree/master/apps */
/*
 * snmpstatus.c - retrieves a fixed set of management information from
 * a network entity.
 *
 */
/***********************************************************************
        Copyright 1988, 1989, 1991, 1992 by Carnegie Mellon University

                      All Rights Reserved

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appear in all copies and that
both that copyright notice and this permission notice appear in
supporting documentation, and that the name of CMU not be
used in advertising or publicity pertaining to distribution of the
software without specific, written prior permission.

CMU DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL
CMU BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
SOFTWARE.
******************************************************************/
#include <net-snmp/net-snmp-config.h>

#ifdef HAVE_STDLIB_H
#include <stdlib.h>
#endif
#ifdef HAVE_UNISTD_H
#include <unistd.h>
#endif
#ifdef HAVE_STRING_H
#include <string.h>
#else
#include <strings.h>
#endif
#include <sys/types.h>
#ifdef HAVE_NETINET_IN_H
#include <netinet/in.h>
#endif
#include <ctype.h>
#include <stdio.h>
#ifdef TIME_WITH_SYS_TIME
#include <sys/time.h>
#include <time.h>
#else
#ifdef HAVE_SYS_TIME_H
#include <sys/time.h>
#else
#include <time.h>
#endif
#endif
#ifdef HAVE_SYS_SELECT_H
#include <sys/select.h>
#endif
#ifdef HAVE_NETDB_H
#include <netdb.h>
#endif
#ifdef HAVE_ARPA_INET_H
#include <arpa/inet.h>
#endif

#include <net-snmp/net-snmp-includes.h>
#include <net-snmp/utilities.h>

#include <cstring>
#include <memory>
#include <mutex>
#include <sstream>
#include <string>
#include <vector>

#include "exceptionsbase.h"
#include "helpers.h"
#include "snmpstatus.h"
#include "thread_safety.h"

#define NETSNMP_DS_APP_DONT_FIX_PDUS 0

namespace {

oid objid_sysDescr[] = {1, 3, 6, 1, 2, 1, 1, 1, 0};
size_t length_sysDescr = OID_LENGTH(objid_sysDescr);
oid objid_sysUpTime[] = {1, 3, 6, 1, 2, 1, 1, 3, 0};
size_t length_sysUpTime = OID_LENGTH(objid_sysUpTime);
oid objid_ifOperStatus[] = {1, 3, 6, 1, 2, 1, 2, 2, 1, 8};
size_t length_ifOperStatus = OID_LENGTH(objid_ifOperStatus);
oid objid_ifInUCastPkts[] = {1, 3, 6, 1, 2, 1, 2, 2, 1, 11};
size_t length_ifInUCastPkts = OID_LENGTH(objid_ifInUCastPkts);
oid objid_ifInNUCastPkts[] = {1, 3, 6, 1, 2, 1, 2, 2, 1, 12};
size_t length_ifInNUCastPkts = OID_LENGTH(objid_ifInNUCastPkts);
oid objid_ifOutUCastPkts[] = {1, 3, 6, 1, 2, 1, 2, 2, 1, 17};
size_t length_ifOutUCastPkts = OID_LENGTH(objid_ifOutUCastPkts);
oid objid_ifOutNUCastPkts[] = {1, 3, 6, 1, 2, 1, 2, 2, 1, 18};
size_t length_ifOutNUCastPkts = OID_LENGTH(objid_ifOutNUCastPkts);
oid objid_ipInReceives[] = {1, 3, 6, 1, 2, 1, 4, 3, 0};
size_t length_ipInReceives = OID_LENGTH(objid_ipInReceives);
oid objid_ipOutRequests[] = {1, 3, 6, 1, 2, 1, 4, 10, 0};
size_t length_ipOutRequests = OID_LENGTH(objid_ipOutRequests);

void snmpstatus_optProc(int, char *const *, int opt) {
   switch (opt) {
      case 'C':
         while (*optarg) {
            switch (*optarg++) {
               case 'f':
                  netsnmp_ds_toggle_boolean(NETSNMP_DS_APPLICATION_ID,
                                            NETSNMP_DS_APP_DONT_FIX_PDUS);
                  break;
               default:
                  throw ParseErrorBase("Unknown flag passed to -C: " + std::string(1, optarg[-1]) +
                                       "\n");
            }
         }
         break;
   }
}

struct SessionCleanupGuard {
   netsnmp_session *session = nullptr;
   bool active = false;
   ~SessionCleanupGuard() {
      if (active && session) {
         netsnmp_cleanup_session(session);
      }
   }
};

std::string format_packet_error(netsnmp_pdu const *response) {
   std::string err_msg =
       "Error in packet.\nReason: " + std::string(snmp_errstring(response->errstat)) + "\n";
   if (response->errindex != 0) {
      err_msg += "Failed object: ";
      int count = 1;
      netsnmp_variable_list *vars = response->variables;
      for (; vars && count != response->errindex; vars = vars->next_variable, count++) {
         /*EMPTY*/
      }
      if (vars) {
         err_msg += print_objid_to_string(vars->name, vars->name_length);
      }
      err_msg += "\n";
   }
   return err_msg;
}

} // namespace

std::vector<std::string> snmpstatus(std::vector<std::string> const &args,
                                    std::string const &init_app_name) {
   netsnmp_thread_init(init_app_name);

   int argc = 0;
   std::unique_ptr<char *[], Deleter> argv = create_argv(args, argc);
   std::vector<std::string> return_vector;

   netsnmp_session session;
   std::unique_ptr<void, SnmpSingleSessionCloser> ss;
   netsnmp_pdu *pdu = nullptr;
   netsnmp_pdu *response = nullptr;
   netsnmp_variable_list *vars = nullptr;
   netsnmp_transport *transport = nullptr;
   std::string sysdescr;
   u_long uptime = 0;
   int status = -1;
   int ipin = 0, ipout = 0, ipackets = 0, opackets = 0;
   int good_var = 0;
   int down_interfaces = 0;
   char buf[40];
   int interfaces = 0;
   int dont_fix_pdus = 0;

   SOCK_STARTUP;
   SockCleanupGuard sock_cleanup_guard;
   SessionCleanupGuard session_cleanup_guard;

   {
      std::lock_guard<std::mutex> setup_lock(g_netsnmp_setup_mutex);

      netsnmp_register_loghandler(NETSNMP_LOGHANDLER_NONE, 0);
      netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_MIB_WARNINGS, 0);
      switch (snmp_parse_args(argc, argv.get(), &session, "C:", snmpstatus_optProc)) {
         case NETSNMP_PARSE_ARGS_ERROR:
            throw ParseErrorBase("NETSNMP_PARSE_ARGS_ERROR");

         case NETSNMP_PARSE_ARGS_SUCCESS_EXIT:
            throw ParseErrorBase("NETSNMP_PARSE_ARGS_SUCCESS_EXIT");

         case NETSNMP_PARSE_ARGS_ERROR_USAGE:
            throw ParseErrorBase("NETSNMP_PARSE_ARGS_ERROR_USAGE");

         default:
            break;
      }

      session_cleanup_guard.session = &session;
      session_cleanup_guard.active = true;

      dont_fix_pdus =
          netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_APP_DONT_FIX_PDUS);
   }

   /*
    * open an SNMP session
    */
   ss.reset(snmp_sess_open(&session));
   if (!ss) {
      snmp_sess_perror_exception("snmpstatus", &session);
   }

   /*
    * create PDU for GET request and add object names to request
    */
   pdu = snmp_pdu_create(SNMP_MSG_GET);
   snmp_add_null_var(pdu, objid_sysDescr, length_sysDescr);
   snmp_add_null_var(pdu, objid_sysUpTime, length_sysUpTime);
   snmp_add_null_var(pdu, objid_ipInReceives, length_ipInReceives);
   snmp_add_null_var(pdu, objid_ipOutRequests, length_ipOutRequests);

retry:
   status = snmp_sess_synch_response(static_cast<struct session_list *>(ss.get()), pdu, &response);
   if (status == STAT_SUCCESS) {
      snmp_check_null_response(response);
      if (response->errstat == SNMP_ERR_NOERROR) {
         for (vars = response->variables; vars; vars = vars->next_variable) {
            if (vars->name_length == length_sysDescr &&
                !std::memcmp(objid_sysDescr, vars->name, sizeof(objid_sysDescr)) &&
                vars->val.string) {
               sysdescr.assign(reinterpret_cast<char const *>(vars->val.string), vars->val_len);
            }
            if (vars->name_length == length_sysUpTime &&
                !std::memcmp(objid_sysUpTime, vars->name, sizeof(objid_sysUpTime)) &&
                vars->val.integer) {
               uptime = *vars->val.integer;
            }
            if (vars->name_length == length_ipInReceives &&
                !std::memcmp(objid_ipInReceives, vars->name, sizeof(objid_ipInReceives)) &&
                vars->val.integer) {
               ipin = static_cast<int>(*vars->val.integer);
            }
            if (vars->name_length == length_ipOutRequests &&
                !std::memcmp(objid_ipOutRequests, vars->name, sizeof(objid_ipOutRequests)) &&
                vars->val.integer) {
               ipout = static_cast<int>(*vars->val.integer);
            }
         }
      } else {
         std::string err_msg = format_packet_error(response);

         /*
          * retry if the errored variable was successfully removed
          */
         if (!dont_fix_pdus) {
            pdu = snmp_fix_pdu(response, SNMP_MSG_GET);
            snmp_free_pdu(response);
            response = nullptr;
            if (pdu != nullptr) {
               goto retry;
            }
         }
         snmp_free_pdu(response);
         response = nullptr;
         throw PacketErrorBase(err_msg);
      }
   } else if (status == STAT_TIMEOUT) {
      std::string peer = session.peername ? session.peername : "";
      throw TimeoutErrorBase("Timeout: No Response from " + peer + "\n");
   } else {
      snmp_single_sess_perror_exception("snmpstatus", ss.get());
   }

   if (!response) {
      throw PacketErrorBase("Received null SNMP response in snmpstatus");
   }

   std::unique_ptr<netsnmp_pdu, SnmpPduDeleter> response_guard(response);
   response = nullptr;

   transport = snmp_sess_transport(static_cast<struct session_list *>(ss.get()));
   std::string addr_str = "<UNKNOWN>";
   if (transport != nullptr && transport->f_fmtaddr != nullptr) {
      char *addr_cstr = transport->f_fmtaddr(transport, response_guard->transport_data,
                                             response_guard->transport_data_length);
      if (addr_cstr != nullptr) {
         addr_str = addr_cstr;
         free(addr_cstr);
      }
   }
   return_vector.push_back("[" + addr_str + "]=>[" + sysdescr +
                           "] Up: " + std::string(uptime_string(uptime, buf)));
   response_guard.reset();

   /*
    * create PDU for GETNEXT request and add object names to request
    */
   pdu = snmp_pdu_create(SNMP_MSG_GETNEXT);
   snmp_add_null_var(pdu, objid_ifOperStatus, length_ifOperStatus);
   snmp_add_null_var(pdu, objid_ifInUCastPkts, length_ifInUCastPkts);
   snmp_add_null_var(pdu, objid_ifInNUCastPkts, length_ifInNUCastPkts);
   snmp_add_null_var(pdu, objid_ifOutUCastPkts, length_ifOutUCastPkts);
   snmp_add_null_var(pdu, objid_ifOutNUCastPkts, length_ifOutNUCastPkts);

   good_var = 5;
   interfaces = 0;
   while (good_var == 5) {
      good_var = 0;
      status =
          snmp_sess_synch_response(static_cast<struct session_list *>(ss.get()), pdu, &response);
      if (status == STAT_SUCCESS) {
         snmp_check_null_response(response);
         std::unique_ptr<netsnmp_pdu, SnmpPduDeleter> loop_response_guard(response);
         response = nullptr;

         if (loop_response_guard->errstat == SNMP_ERR_NOERROR) {
            pdu = snmp_pdu_create(SNMP_MSG_GETNEXT);
            for (vars = loop_response_guard->variables; vars; vars = vars->next_variable) {
               if ((vars->type & 0xF0) == 0x80) {
                  continue;
               }
               if (vars->name_length >= length_ifOperStatus &&
                   !std::memcmp(objid_ifOperStatus, vars->name, sizeof(objid_ifOperStatus)) &&
                   vars->type == ASN_INTEGER && vars->val.integer) {
                  if (*vars->val.integer != MIB_IFSTATUS_UP) {
                     down_interfaces++;
                  }
                  snmp_add_null_var(pdu, vars->name, vars->name_length);
                  good_var++;
               } else if (vars->name_length >= length_ifInUCastPkts &&
                          !std::memcmp(objid_ifInUCastPkts, vars->name,
                                       sizeof(objid_ifInUCastPkts)) &&
                          vars->type == ASN_COUNTER && vars->val.integer) {
                  ipackets += static_cast<int>(*vars->val.integer);
                  snmp_add_null_var(pdu, vars->name, vars->name_length);
                  good_var++;
               } else if (vars->name_length >= length_ifInNUCastPkts &&
                          !std::memcmp(objid_ifInNUCastPkts, vars->name,
                                       sizeof(objid_ifInNUCastPkts)) &&
                          vars->type == ASN_COUNTER && vars->val.integer) {
                  ipackets += static_cast<int>(*vars->val.integer);
                  snmp_add_null_var(pdu, vars->name, vars->name_length);
                  good_var++;
               } else if (vars->name_length >= length_ifOutUCastPkts &&
                          !std::memcmp(objid_ifOutUCastPkts, vars->name,
                                       sizeof(objid_ifOutUCastPkts)) &&
                          vars->type == ASN_COUNTER && vars->val.integer) {
                  opackets += static_cast<int>(*vars->val.integer);
                  snmp_add_null_var(pdu, vars->name, vars->name_length);
                  good_var++;
               } else if (vars->name_length >= length_ifOutNUCastPkts &&
                          !std::memcmp(objid_ifOutNUCastPkts, vars->name,
                                       sizeof(objid_ifOutNUCastPkts)) &&
                          vars->type == ASN_COUNTER && vars->val.integer) {
                  opackets += static_cast<int>(*vars->val.integer);
                  snmp_add_null_var(pdu, vars->name, vars->name_length);
                  good_var++;
               }
            }
            if (good_var == 5) {
               interfaces++;
            } else {
               snmp_free_pdu(pdu);
               pdu = nullptr;
            }
         } else {
            throw PacketErrorBase(format_packet_error(loop_response_guard.get()));
         }
      } else if (status == STAT_TIMEOUT) {
         std::string peer = session.peername ? session.peername : "";
         throw TimeoutErrorBase("Timeout: No Response from " + peer + "\n");
      } else {
         snmp_single_sess_perror_exception("snmpstatus", ss.get());
      }
   }

   std::ostringstream stats_oss;
   stats_oss << "Interfaces: " << interfaces << ", Recv/Trans packets: " << ipackets << "/"
             << opackets << " | IP: " << ipin << "/" << ipout;
   return_vector.push_back(stats_oss.str());

   if (down_interfaces > 0) {
      std::ostringstream down_oss;
      down_oss << down_interfaces << " interface" << (down_interfaces > 1 ? "s are" : " is")
               << " down!";
      return_vector.push_back(down_oss.str());
   }

   ss.reset();
   return return_vector;
}
