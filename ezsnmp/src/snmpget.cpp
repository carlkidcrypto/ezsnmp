/* straight copy from https://github.com/net-snmp/net-snmp/tree/master/apps */
/*
 * snmpget.c - send snmp GET requests to a network entity.
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

#define NETSNMP_DS_APP_DONT_FIX_PDUS 0

#include "exceptionsbase.h"
#include "helpers.h"
#include "snmpget.h"

void snmpget_optProc(int argc, char *const *argv, int opt) {
   switch (opt) {
      case 'C':
         while (*optarg) {
            switch (*optarg++) {
               case 'f':
                  netsnmp_ds_toggle_boolean(NETSNMP_DS_APPLICATION_ID,
                                            NETSNMP_DS_APP_DONT_FIX_PDUS);
                  break;
               default:
                  std::string err_msg =
                      "Unknown flag passed to -C: " + std::string(1, optarg[-1]) + "\n";
                  throw ParseErrorBase(err_msg);
            }
         }
         break;
   }
}

void snmpget_usage(void) {
   fprintf(stderr, "USAGE: snmpget ");
   snmp_parse_args_usage(stderr);
   fprintf(stderr, " OID [OID]...\n\n");
   snmp_parse_args_descriptions(stderr);
   fprintf(stderr, "  -C APPOPTS\t\tSet various application specific behaviours:\n");
   fprintf(stderr, "\t\t\t  f:  do not fix errors and retry the request\n");
}

std::vector<Result> snmpget(std::vector<std::string> const &args) {
   /* completely disable logging otherwise it will default to stderr */
   netsnmp_register_loghandler(NETSNMP_LOGHANDLER_NONE, 0);

   int argc;
   std::unique_ptr<char *[]> argv = create_argv(args, argc);
   std::vector<std::string> return_vector;

   netsnmp_session session, *ss;
   netsnmp_pdu *pdu;
   netsnmp_pdu *response;
   netsnmp_variable_list *vars;
   int arg;
   int count;
   int current_name = 0;
   char *names[SNMP_MAX_CMDLINE_OIDS];
   oid name[MAX_OID_LEN];
   size_t name_length;
   int status;
   int failures = 0;

   SOCK_STARTUP;

   /*
    * get the common command line arguments
    */
   switch (arg = snmp_parse_args(argc, argv.get(), &session, "C:", snmpget_optProc)) {
      case NETSNMP_PARSE_ARGS_ERROR:
         throw ParseErrorBase("NETSNMP_PARSE_ARGS_ERROR");

      case NETSNMP_PARSE_ARGS_SUCCESS_EXIT:
         throw ParseErrorBase("NETSNMP_PARSE_ARGS_SUCCESS_EXIT");

      case NETSNMP_PARSE_ARGS_ERROR_USAGE:
         throw ParseErrorBase("NETSNMP_PARSE_ARGS_ERROR_USAGE");

      default:
         break;
   }

   if (arg >= argc) {
      std::string err_msg = "Missing object name\n";
      throw GenericErrorBase(err_msg);
   }
   if ((argc - arg) > SNMP_MAX_CMDLINE_OIDS) {
      std::string err_msg =
          "Too many object identifiers specified. "
          "Only " +
          std::to_string(SNMP_MAX_CMDLINE_OIDS) + " allowed in one request.\n";
      throw GenericErrorBase(err_msg);
   }

   /*
    * get the object names
    */
   for (; arg < argc; arg++) {
      names[current_name++] = argv[arg];
   }

   /*
    * Open an SNMP session.
    */
   ss = snmp_open(&session);
   if (ss == NULL) {
      /*
       * diagnose snmp_open errors with the input netsnmp_session pointer
       */
      snmp_sess_perror_exception("snmpget", &session);
   }

   /*
    * Create PDU for GET request and add object names to request.
    */
   pdu = snmp_pdu_create(SNMP_MSG_GET);
   for (count = 0; count < current_name; count++) {
      name_length = MAX_OID_LEN;
      if (!snmp_parse_oid(names[count], name, &name_length)) {
         snmp_perror_exception(names[count]);
         failures++;
      } else {
         snmp_add_null_var(pdu, name, name_length);
      }
   }
   if (failures) {
      snmp_free_pdu(pdu);
      snmp_close(ss);
      return parse_results(return_vector);
   }

   /*
    * Perform the request.
    *
    * If the Get Request fails, note the OID that caused the error,
    * "fix" the PDU (removing the error-prone OID) and retry.
    */
retry:
   status = snmp_synch_response(ss, pdu, &response);
   if (status == STAT_SUCCESS) {
      if (response->errstat == SNMP_ERR_NOERROR) {
         for (vars = response->variables; vars; vars = vars->next_variable) {
            auto str_value = print_variable_to_string(vars->name, vars->name_length, vars);
            return_vector.push_back(str_value);
         }
      } else {
         std::string err_msg =
             "Error in packet\nReason: " + std::string(snmp_errstring(response->errstat)) + "\n";

         if (response->errindex != 0) {
            err_msg = err_msg + "Failed object: ";
            for (count = 1, vars = response->variables; vars && count != response->errindex;
                 vars = vars->next_variable, count++)
               /*EMPTY*/;
            if (vars) {
               err_msg = err_msg + print_objid_to_string(vars->name, vars->name_length);
            }
            err_msg = err_msg + "\n";
         }

         /*
          * retry if the errored variable was successfully removed
          */
         if (!netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_APP_DONT_FIX_PDUS)) {
            pdu = snmp_fix_pdu(response, SNMP_MSG_GET);
            snmp_free_pdu(response);
            response = NULL;
            if (pdu != NULL) {
               goto retry;
            }
         }
         throw PacketErrorBase(err_msg);

      } /* endif -- SNMP_ERR_NOERROR */
   } else if (status == STAT_TIMEOUT) {
      std::string err_msg = "Timeout: No Response from " + std::string(session.peername) + ".\n";
      throw TimeoutErrorBase(err_msg);
   } else { /* status == STAT_ERROR */
      snmp_sess_perror_exception("snmpget", ss);

   } /* endif -- STAT_SUCCESS */

   if (response) {
      snmp_free_pdu(response);
   }

   netsnmp_cleanup_session(&session);
   SOCK_CLEANUP;
   return parse_results(return_vector);
} /* end main() */
