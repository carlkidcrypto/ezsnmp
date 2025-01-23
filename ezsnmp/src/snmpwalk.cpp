/* straight copy from https://github.com/net-snmp/net-snmp/tree/master/apps */
/*
 * snmpwalk.c - send snmp GETNEXT requests to a network entity, walking a
 * subtree.
 *
 */
/**********************************************************************
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
#define NETSNMP_DS_WALK_TIME_RESULTS 4
#define NETSNMP_DS_WALK_DONT_GET_REQUESTED 5
#define NETSNMP_DS_WALK_TIME_RESULTS_SINGLE 6

oid objid_mib[] = {1, 3, 6, 1, 2, 1};
int numprinted = 0;

char *end_name = NULL;

#include "exceptionsbase.h"
#include "helpers.h"
#include "snmpwalk.h"

void snmpwalk_usage(void) {
   fprintf(stderr, "USAGE: snmpwalk ");
   snmp_parse_args_usage(stderr);
   fprintf(stderr, " [OID]\n\n");
   snmp_parse_args_descriptions(stderr);
   fprintf(stderr, "  -C APPOPTS\t\tSet various application specific behaviours:\n");
   fprintf(stderr, "\t\t\t  p:  print the number of variables found\n");
   fprintf(stderr, "\t\t\t  i:  include given OID in the search range\n");
   fprintf(stderr,
           "\t\t\t  I:  don't include the given OID, even if no results "
           "are returned\n");
   fprintf(stderr, "\t\t\t  c:  do not check returned OIDs are increasing\n");
   fprintf(stderr, "\t\t\t  t:  Display wall-clock time to complete the walk\n");
   fprintf(stderr, "\t\t\t  T:  Display wall-clock time to complete each request\n");
   fprintf(stderr, "\t\t\t  E {OID}:  End the walk at the specified OID\n");
}

std::vector<std::string> snmpwalk_snmp_get_and_print(netsnmp_session *ss,
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
         numprinted++;
         auto str_value = print_variable_to_string(vars->name, vars->name_length, vars);
         str_values.push_back(str_value);
      }
   }
   if (response) {
      snmp_free_pdu(response);
   }

   return str_values;
}

void snmpwalk_optProc(int argc, char *const *argv, int opt) {
   switch (opt) {
      case 'C':
         while (*optarg) {
            switch (*optarg++) {
               case 'i':
                  netsnmp_ds_toggle_boolean(NETSNMP_DS_APPLICATION_ID,
                                            NETSNMP_DS_WALK_INCLUDE_REQUESTED);
                  break;

               case 'I':
                  netsnmp_ds_toggle_boolean(NETSNMP_DS_APPLICATION_ID,
                                            NETSNMP_DS_WALK_DONT_GET_REQUESTED);
                  break;

               case 'p':
                  netsnmp_ds_toggle_boolean(NETSNMP_DS_APPLICATION_ID,
                                            NETSNMP_DS_WALK_PRINT_STATISTICS);
                  break;

               case 'c':
                  netsnmp_ds_toggle_boolean(NETSNMP_DS_APPLICATION_ID,
                                            NETSNMP_DS_WALK_DONT_CHECK_LEXICOGRAPHIC);
                  break;

               case 't':
                  netsnmp_ds_toggle_boolean(NETSNMP_DS_APPLICATION_ID,
                                            NETSNMP_DS_WALK_TIME_RESULTS);
                  break;

               case 'E':
                  end_name = argv[optind++];
                  break;

               case 'T':
                  netsnmp_ds_toggle_boolean(NETSNMP_DS_APPLICATION_ID,
                                            NETSNMP_DS_WALK_TIME_RESULTS_SINGLE);
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

std::vector<Result> snmpwalk(std::vector<std::string> const &args) {
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
   oid end_oid[MAX_OID_LEN];
   size_t end_len = 0;
   int count;
   int running;
   int status = STAT_ERROR;
   int check;
   struct timeval tv1, tv2, tv_a, tv_b;

   SOCK_STARTUP;

   netsnmp_ds_register_config(ASN_BOOLEAN, "snmpwalk", "includeRequested",
                              NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_INCLUDE_REQUESTED);

   netsnmp_ds_register_config(ASN_BOOLEAN, "snmpwalk", "excludeRequested",
                              NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_DONT_GET_REQUESTED);

   netsnmp_ds_register_config(ASN_BOOLEAN, "snmpwalk", "printStatistics", NETSNMP_DS_APPLICATION_ID,
                              NETSNMP_DS_WALK_PRINT_STATISTICS);

   netsnmp_ds_register_config(ASN_BOOLEAN, "snmpwalk", "dontCheckOrdering",
                              NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_DONT_CHECK_LEXICOGRAPHIC);

   netsnmp_ds_register_config(ASN_BOOLEAN, "snmpwalk", "timeResults", NETSNMP_DS_APPLICATION_ID,
                              NETSNMP_DS_WALK_TIME_RESULTS);

   netsnmp_ds_register_config(ASN_BOOLEAN, "snmpwalk", "timeResultsSingle",
                              NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_TIME_RESULTS_SINGLE);

   /*
    * get the common command line arguments
    */
   switch (arg = snmp_parse_args(argc, argv.get(), &session, "C:", snmpwalk_optProc)) {
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
      }
   } else {
      /*
       * use default value
       */
      memmove(root, objid_mib, sizeof(objid_mib));
      rootlen = OID_LENGTH(objid_mib);
   }

   /*
    * If we've been given an explicit end point,
    *  then convert this to an OID, otherwise
    *  move to the next sibling of the start.
    */
   if (end_name) {
      end_len = MAX_OID_LEN;
      if (snmp_parse_oid(end_name, end_oid, &end_len) == NULL) {
         snmp_perror_exception(end_name);
      }
   } else {
      memmove(end_oid, root, rootlen * sizeof(oid));
      end_len = rootlen;
      end_oid[end_len - 1]++;
   }

   /*
    * open an SNMP session
    */
   ss = snmp_open(&session);
   if (ss == NULL) {
      /*
       * diagnose snmp_open errors with the input netsnmp_session pointer
       */
      snmp_sess_perror_exception("snmpwalk", &session);
   }

   /*
    * get first object to start walk
    */
   memmove(name, root, rootlen * sizeof(oid));
   name_length = rootlen;

   running = 1;

   check =
       !netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_DONT_CHECK_LEXICOGRAPHIC);
   if (netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_INCLUDE_REQUESTED)) {
      auto retval = snmpwalk_snmp_get_and_print(ss, root, rootlen);

      for (auto const &item : retval) {
         return_vector.push_back(item);
      }
   }

   if (netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_TIME_RESULTS)) {
      netsnmp_get_monotonic_clock(&tv1);
   }

   while (running) {
      /*
       * create PDU for GETNEXT request and add object name to request
       */
      pdu = snmp_pdu_create(SNMP_MSG_GETNEXT);
      snmp_add_null_var(pdu, name, name_length);

      /*
       * do the request
       */
      if (netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_TIME_RESULTS_SINGLE)) {
         netsnmp_get_monotonic_clock(&tv_a);
      }
      status = snmp_synch_response(ss, pdu, &response);
      if (status == STAT_SUCCESS) {
         if (netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID,
                                    NETSNMP_DS_WALK_TIME_RESULTS_SINGLE)) {
            netsnmp_get_monotonic_clock(&tv_b);
         }
         if (response->errstat == SNMP_ERR_NOERROR) {
            /*
             * check resulting variables
             */
            for (vars = response->variables; vars; vars = vars->next_variable) {
               if (snmp_oid_compare(end_oid, end_len, vars->name, vars->name_length) <= 0) {
                  /*
                   * not part of this subtree
                   */
                  running = 0;
                  continue;
               }
               numprinted++;
               if (netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID,
                                          NETSNMP_DS_WALK_TIME_RESULTS_SINGLE)) {
                  fprintf(stdout, "%f s: ",
                          (double)(tv_b.tv_usec - tv_a.tv_usec) / 1000000 +
                              (double)(tv_b.tv_sec - tv_a.tv_sec));
               }

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
                  memmove((char *)name, (char *)vars->name, vars->name_length * sizeof(oid));
                  name_length = vars->name_length;
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
         snmp_sess_perror_exception("snmpwalk", ss);
      }
      if (response) {
         snmp_free_pdu(response);
      }
   }
   if (netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_TIME_RESULTS)) {
      netsnmp_get_monotonic_clock(&tv2);
   }

   if (numprinted == 0 && status == STAT_SUCCESS) {
      /*
       * no printed successful results, which may mean we were
       * pointed at an only existing instance.  Attempt a GET, just
       * for get measure.
       */
      if (!netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_DONT_GET_REQUESTED)) {
         auto retval = snmpwalk_snmp_get_and_print(ss, root, rootlen);

         for (auto const &item : retval) {
            return_vector.push_back(item);
         }
      }
   }
   snmp_close(ss);

   if (netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_PRINT_STATISTICS)) {
      printf("Variables found: %d\n", numprinted);
   }
   if (netsnmp_ds_get_boolean(NETSNMP_DS_APPLICATION_ID, NETSNMP_DS_WALK_TIME_RESULTS)) {
      fprintf(stderr, "Total traversal time = %f seconds\n",
              (double)(tv2.tv_usec - tv1.tv_usec) / 1000000 + (double)(tv2.tv_sec - tv1.tv_sec));
   }

   netsnmp_cleanup_session(&session);
   SOCK_CLEANUP;
   return parse_results(return_vector);
}