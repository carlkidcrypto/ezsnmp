/* straight copy from https://github.com/net-snmp/net-snmp/tree/master/apps */
/*
 * snmpbulkwalk.c - send SNMPv2 Bulk requests to a network entity, walking a
 * subtree.
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

#define NETSNMP_DS_WALK_INCLUDE_REQUESTED 1
#define NETSNMP_DS_WALK_PRINT_STATISTICS 2
#define NETSNMP_DS_WALK_DONT_CHECK_LEXICOGRAPHIC 3

oid snmpbulkwalk_objid_mib[] = {1, 3, 6, 1, 2, 1};
int snmpbulkwalk_numprinted = 0;
int snmpbulkwalk_reps = 10, snmpbulkwalk_non_reps = 0;

#include "exceptionsbase.h"
#include "helpers.h"
#include "snmpbulkwalk.h"

void snmpbulkwalk_usage(void) {
   fprintf(stderr, "USAGE: snmpbulkwalk ");
   snmp_parse_args_usage(stderr);
   fprintf(stderr, " [OID]\n\n");
   snmp_parse_args_descriptions(stderr);
   fprintf(stderr, "  -C APPOPTS\t\tSet various application specific behaviours:\n");
   fprintf(stderr, "\t\t\t  c:       do not check returned OIDs are increasing\n");
   fprintf(stderr, "\t\t\t  i:       include given OIDs in the search range\n");
   fprintf(stderr, "\t\t\t  n<NUM>:  set non-repeaters to <NUM>\n");
   fprintf(stderr, "\t\t\t  p:       print the number of variables found\n");
   fprintf(stderr, "\t\t\t  r<NUM>:  set max-repeaters to <NUM>\n");
}

std::vector<std::string> snmpbulkwalk_snmp_get_and_print(netsnmp_session *ss,
                                                         oid *theoid,
                                                         size_t theoid_len) {
   std::vector<std::string> str_values;

   netsnmp_pdu *pdu, *response;
   netsnmp_variable_list *vars;
   int status;

   pdu = snmp_pdu_create(SNMP_MSG_GET);
   snmp_add_null_var(pdu, theoid, theoid_len);

   status = snmp_synch_response(ss, pdu, &response);
   if (status == STAT_SUCCESS && response->errstat == SNMP_ERR_NOERROR) {
      for (vars = response->variables; vars; vars = vars->next_variable) {
         snmpbulkwalk_numprinted++;
         auto str_value = print_variable_to_string(vars->name, vars->name_length, vars);
         str_values.push_back(str_value);
      }
   }
   if (response) {
      snmp_free_pdu(response);
   }

   return str_values;
}

void snmpbulkwalk_optProc(int argc, char *const *argv, int opt) {
   char *endptr = NULL;

   switch (opt) {
      case 'C':
         while (*optarg) {
            switch (*optarg++) {
               case 'c':
                  netsnmp_ds_toggle_boolean(NETSNMP_DS_APPLICATION_ID,
                                            NETSNMP_DS_WALK_DONT_CHECK_LEXICOGRAPHIC);
                  break;

               case 'i':
                  netsnmp_ds_toggle_boolean(NETSNMP_DS_APPLICATION_ID,
                                            NETSNMP_DS_WALK_INCLUDE_REQUESTED);
                  break;

               case 'n':
               case 'r':
                  if (*(optarg - 1) == 'r') {
                     snmpbulkwalk_reps = strtol(optarg, &endptr, 0);
                  } else {
                     snmpbulkwalk_non_reps = strtol(optarg, &endptr, 0);
                  }

                  if (endptr == optarg) {
                     /*
                      * No number given -- error.
                      */
                     snmpbulkwalk_usage();
                     exit(1);
                  } else {
                     optarg = endptr;
                     if (isspace((unsigned char)(*optarg))) {
                        return;
                     }
                  }
                  break;

               case 'p':
                  netsnmp_ds_toggle_boolean(NETSNMP_DS_APPLICATION_ID,
                                            NETSNMP_DS_WALK_PRINT_STATISTICS);
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

std::vector<Result> snmpbulkwalk(std::vector<std::string> const &args) {
   /* completely disable logging otherwise it will default to stderr */
   netsnmp_register_loghandler(NETSNMP_LOGHANDLER_NONE, 0);

   int argc;
   std::unique_ptr<char *[]> argv = create_argv(args, argc);

   std::vector<std::string> return_vector;
   netsnmp_session session, *ss;
   netsnmp_pdu *pdu, *response;
   netsnmp_variable_list *vars;
   int arg;
   oid name[MAX_OID_LEN];
   size_t name_length;
   oid root[MAX_OID_LEN];
   size_t rootlen;
   int count;
   int running;
   int status = STAT_ERROR;
   int check;

   SOCK_STARTUP;

   netsnmp_ds_register_config(ASN_BOOLEAN, "snmpwalk", "includeRequested",
                              NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_INCLUDE_REQUESTED);
   netsnmp_ds_register_config(ASN_BOOLEAN, "snmpwalk", "printStatistics", NETSNMP_DS_APPLICATION_ID,
                              NETSNMP_DS_WALK_PRINT_STATISTICS);
   netsnmp_ds_register_config(ASN_BOOLEAN, "snmpwalk", "dontCheckOrdering",
                              NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_DONT_CHECK_LEXICOGRAPHIC);

   /*
    * get the common command line arguments
    */
   switch (arg = snmp_parse_args(argc, argv.get(), &session, "C:", snmpbulkwalk_optProc)) {
      case NETSNMP_PARSE_ARGS_ERROR:
         throw ParseErrorBase("NETSNMP_PARSE_ARGS_ERROR");

      case NETSNMP_PARSE_ARGS_SUCCESS_EXIT:
         throw ParseErrorBase("NETSNMP_PARSE_ARGS_SUCCESS_EXIT");

      case NETSNMP_PARSE_ARGS_ERROR_USAGE:
         throw ParseErrorBase("NETSNMP_PARSE_ARGS_ERROR_USAGE");

      default:
         break;
   }

   /*
    * get the initial object and subtree
    */
   if (arg < argc) {
      /*
       * specified on the command line
       */
      rootlen = MAX_OID_LEN;
      if (snmp_parse_oid(argv[arg], root, &rootlen) == NULL) {
         snmp_perror_exception(argv[arg]);
         return parse_results(return_vector);
      }
   } else {
      /*
       * use default value
       */
      memmove(root, snmpbulkwalk_objid_mib, sizeof(snmpbulkwalk_objid_mib));
      rootlen = OID_LENGTH(snmpbulkwalk_objid_mib);
   }

   /*
    * open an SNMP session
    */
   ss = snmp_open(&session);
   if (ss == NULL) {
      /*
       * diagnose snmp_open errors with the input netsnmp_session pointer
       */
      snmp_sess_perror_exception("snmpbulkwalk", &session);
      return parse_results(return_vector);
   }

   /*
    * setup initial object name
    */
   memmove(name, root, rootlen * sizeof(oid));
   name_length = rootlen;

   running = 1;

   check =
       !netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_DONT_CHECK_LEXICOGRAPHIC);
   if (netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_INCLUDE_REQUESTED)) {
      auto retval = snmpbulkwalk_snmp_get_and_print(ss, root, rootlen);

      for (auto const &item : retval) {
         return_vector.push_back(item);
      }
   }

   while (running) {
      /*
       * create PDU for GETBULK request and add object name to request
       */
      pdu = snmp_pdu_create(SNMP_MSG_GETBULK);
      pdu->non_repeaters = snmpbulkwalk_non_reps;
      pdu->max_repetitions = snmpbulkwalk_reps; /* fill the packet */
      snmp_add_null_var(pdu, name, name_length);

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
               if ((vars->name_length < rootlen) ||
                   (memcmp(root, vars->name, rootlen * sizeof(oid)) != 0)) {
                  /*
                   * not part of this subtree
                   */
                  running = 0;
                  continue;
               }
               snmpbulkwalk_numprinted++;
               auto str_value = print_variable_to_string(vars->name, vars->name_length, vars);
               return_vector.push_back(str_value);
               if ((vars->type != SNMP_ENDOFMIBVIEW) && (vars->type != SNMP_NOSUCHOBJECT) &&
                   (vars->type != SNMP_NOSUCHINSTANCE)) {
                  /*
                   * not an exception value
                   */
                  if (check &&
                      snmp_oid_compare(name, name_length, vars->name, vars->name_length) >= 0) {
                     std::string err_msg = "Error: OID not increasing: ";
                     err_msg = err_msg + print_objid_to_string(name, name_length) + " >= ";
                     err_msg =
                         err_msg + print_objid_to_string(vars->name, vars->name_length) + "\n";

                     throw GenericErrorBase(err_msg);
                  }
                  /*
                   * Check if last variable, and if so, save for next request.
                   */
                  if (vars->next_variable == NULL) {
                     memmove(name, vars->name, vars->name_length * sizeof(oid));
                     name_length = vars->name_length;
                  }
               } else {
                  /*
                   * an exception value, so stop
                   */
                  running = 0;
               }
            }
         } else {
            /*
             * error in response, print it
             */
            running = 0;
            if (response->errstat == SNMP_ERR_NOSUCHNAME) {
               // printf("End of MIB\n");
            } else {
               std::string err_msg =
                   "Error in packet\nReason: " + std::string(snmp_errstring(response->errstat)) +
                   "\n";
               if (response->errindex != 0) {
                  err_msg = err_msg + "Failed object: ";
                  for (count = 1, vars = response->variables; vars && count != response->errindex;
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
         snmp_sess_perror_exception("snmpbulkwalk", ss);
      }
      if (response) {
         snmp_free_pdu(response);
      }
   }

   if (snmpbulkwalk_numprinted == 0 && status == STAT_SUCCESS) {
      /*
       * no printed successful results, which may mean we were
       * pointed at an only existing instance.  Attempt a GET, just
       * for get measure.
       */
      auto retval = snmpbulkwalk_snmp_get_and_print(ss, root, rootlen);

      for (auto const &item : retval) {
         return_vector.push_back(item);
      }
   }
   snmp_close(ss);

   if (netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_PRINT_STATISTICS)) {
      printf("Variables found: %d\n", snmpbulkwalk_numprinted);
   }

   netsnmp_cleanup_session(&session);
   SOCK_CLEANUP;
   return parse_results(return_vector);
}
