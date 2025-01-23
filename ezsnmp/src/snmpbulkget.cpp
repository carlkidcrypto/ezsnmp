/* straight copy from https://github.com/net-snmp/net-snmp/tree/master/apps */
/*
 * snmpbulkget.c - send SNMPv2 Bulk requests to a network entity.
 *
 */
/*********************************************************************
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
**********************************************************************/
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
#include <net-snmp/utilities.h>
#include <sys/types.h>
#ifdef HAVE_NETINET_IN_H
#include <netinet/in.h>
#endif
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
#include <ctype.h>
#include <stdio.h>
#ifdef HAVE_NETDB_H
#include <netdb.h>
#endif
#ifdef HAVE_ARPA_INET_H
#include <arpa/inet.h>
#endif

#include <net-snmp/net-snmp-includes.h>

oid snmpbulkget_objid_mib[] = {1, 3, 6, 1, 2, 1};
int max_repetitions = 10;
int non_repeaters = 0;
struct nameStruct {
   oid name[MAX_OID_LEN];
   size_t name_len;
} *name, *namep;
int names;

#include "exceptionsbase.h"
#include "helpers.h"
#include "snmpbulkget.h"

void snmpbulkget_usage(void) {
   fprintf(stderr, "USAGE: snmpbulkget ");
   snmp_parse_args_usage(stderr);
   fprintf(stderr, " OID [OID]...\n\n");
   snmp_parse_args_descriptions(stderr);
   fprintf(stderr, "  -C APPOPTS\t\tSet various application specific behaviours:\n");
   fprintf(stderr, "\t\t\t  n<NUM>:  set non-repeaters to <NUM>\n");
   fprintf(stderr, "\t\t\t  r<NUM>:  set max-repeaters to <NUM>\n");
}

void snmpbulkget_optProc(int argc, char *const *argv, int opt) {
   char *endptr = NULL;

   switch (opt) {
      case 'C':
         while (*optarg) {
            switch (*optarg++) {
               case 'n':
               case 'r':
                  if (*(optarg - 1) == 'r') {
                     max_repetitions = strtol(optarg, &endptr, 0);
                  } else {
                     non_repeaters = strtol(optarg, &endptr, 0);
                  }

                  if (endptr == optarg) {
                     /*
                      * No number given -- error.
                      */
                     snmpbulkget_usage();
                     exit(1);
                  } else {
                     optarg = endptr;
                     if (isspace((unsigned char)(*optarg))) {
                        return;
                     }
                  }
                  break;

               default:
                  std::string err_msg =
                      "Unknown flag passed to -C: " + std::string(1, optarg[-1]) + "\n";
                  throw ParseErrorBase(err_msg);
            }
         }
   }
}

std::vector<Result> snmpbulkget(std::vector<std::string> const &args) {
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
   int status;

   SOCK_STARTUP;

   /*
    * get the common command line arguments
    */
   switch (arg = snmp_parse_args(argc, argv.get(), &session, "C:", snmpbulkget_optProc)) {
      case NETSNMP_PARSE_ARGS_ERROR:
         throw ParseErrorBase("NETSNMP_PARSE_ARGS_ERROR");

      case NETSNMP_PARSE_ARGS_SUCCESS_EXIT:
         throw ParseErrorBase("NETSNMP_PARSE_ARGS_SUCCESS_EXIT");

      case NETSNMP_PARSE_ARGS_ERROR_USAGE:
         throw ParseErrorBase("NETSNMP_PARSE_ARGS_ERROR_USAGE");

      default:
         break;
   }

   names = argc - arg;
   if (names < non_repeaters) {
      fprintf(stderr, "snmpbulkget: need more objects than <nonrep>\n");
      return parse_results(return_vector);
   }

   namep = name = (struct nameStruct *)calloc(names, sizeof(*name));
   while (arg < argc) {
      namep->name_len = MAX_OID_LEN;
      if (snmp_parse_oid(argv[arg], namep->name, &namep->name_len) == NULL) {
         snmp_perror_exception(argv[arg]);
         return parse_results(return_vector);
      }
      arg++;
      namep++;
   }

   /*
    * open an SNMP session
    */
   ss = snmp_open(&session);
   if (ss == NULL) {
      /*
       * diagnose snmp_open errors with the input netsnmp_session pointer
       */
      snmp_sess_perror_exception("snmpbulkget", &session);
      return parse_results(return_vector);
   }

   /*
    * create PDU for GETBULK request and add object name to request
    */
   pdu = snmp_pdu_create(SNMP_MSG_GETBULK);
   pdu->non_repeaters = non_repeaters;
   pdu->max_repetitions = max_repetitions; /* fill the packet */
   for (arg = 0; arg < names; arg++) {
      snmp_add_null_var(pdu, name[arg].name, name[arg].name_len);
   }

   /*
    * do the request
    */
   status = snmp_synch_response(ss, pdu, &response);
   if (status == STAT_SUCCESS) {
      if (response->errstat == SNMP_ERR_NOERROR) {
         /*
          * check resulting variables
          */
         for (vars = response->variables; vars; vars = vars->next_variable) {
            auto str_value = print_variable_to_string(vars->name, vars->name_length, vars);
            return_vector.push_back(str_value);
         }
      } else {
         /*
          * error in response, print it
          */
         if (response->errstat == SNMP_ERR_NOSUCHNAME) {
            // printf("End of MIB.\n");
         } else {
            std::string err_msg =
                "Error in packet\nReason: " + std::string(snmp_errstring(response->errstat)) + "\n";
            if (response->errindex != 0) {
               err_msg = err_msg + "Failed object: ";
               for (count = 1, vars = response->variables; vars && (count != response->errindex);
                    vars = vars->next_variable, count++)
                  /*EMPTY*/;
               if (vars) {
                  err_msg = err_msg + print_objid_to_string(vars->name, vars->name_length);
               }
               err_msg = err_msg + "\n";
               throw PacketErrorBase(err_msg);
            }
         }
      }
   } else if (status == STAT_TIMEOUT) {
      std::string err_msg = "Timeout: No Response from " + std::string(session.peername) + ".\n";
      throw TimeoutErrorBase(err_msg);

   } else { /* status == STAT_ERROR */
      snmp_sess_perror_exception("snmpbulkget", ss);
   }

   if (response) {
      snmp_free_pdu(response);
   }

   snmp_close(ss);

   netsnmp_cleanup_session(&session);
   SOCK_CLEANUP;
   return parse_results(return_vector);
}
