/* straight copy from https://github.com/net-snmp/net-snmp/tree/master/apps */
/*
 * snmpset.c - send snmp SET requests to a network entity.
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

#include "exceptionsbase.h"
#include "helpers.h"
#include "snmpwalk.h"

void snmpset_usage(void) {
   fprintf(stderr, "USAGE: snmpset ");
   snmp_parse_args_usage(stderr);
   fprintf(stderr, " OID TYPE VALUE [OID TYPE VALUE]...\n\n");
   snmp_parse_args_descriptions(stderr);
   fprintf(stderr, "  -C APPOPTS\t\tSet various application specific behaviours:\n");
   fprintf(stderr, "\t\t\t  q:  don't print results on success\n");
   fprintf(stderr, "\n  TYPE: one of i, u, t, a, o, s, x, d, b\n");
   fprintf(stderr, "\ti: INTEGER, u: unsigned INTEGER, t: TIMETICKS, a: IPADDRESS\n");
   fprintf(stderr, "\to: OBJID, s: STRING, x: HEX STRING, d: DECIMAL STRING, b: BITS\n");
#ifdef NETSNMP_WITH_OPAQUE_SPECIAL_TYPES
   fprintf(stderr, "\tU: unsigned int64, I: signed int64, F: float, D: double\n");
#endif /* NETSNMP_WITH_OPAQUE_SPECIAL_TYPES */
}

static int quiet = 0;

void snmpset_optProc(int argc, char *const *argv, int opt) {
   switch (opt) {
      case 'C':
         while (*optarg) {
            switch (*optarg++) {
               case 'q':
                  quiet = 1;
                  break;

               default:
                  std::string err_msg =
                      "Unknown flag passed to -C: " + std::string(1, optarg[-1]) + "\n";
                  throw ParseErrorBase(err_msg);
            }
         }
   }
}

std::vector<Result> snmpset(std::vector<std::string> const &args) {
   /* completely disable logging otherwise it will default to stderr */
   netsnmp_register_loghandler(NETSNMP_LOGHANDLER_NONE, 0);

   int argc;
   std::unique_ptr<char *[]> argv = create_argv(args, argc);
   std::vector<std::string> return_vector;

   netsnmp_session session, *ss;
   netsnmp_pdu *pdu, *response = NULL;
   netsnmp_variable_list *vars;
   int arg;
   int count;
   int current_name = 0;
   int current_type = 0;
   int current_value = 0;
   char *names[SNMP_MAX_CMDLINE_OIDS];
   char types[SNMP_MAX_CMDLINE_OIDS];
   char *values[SNMP_MAX_CMDLINE_OIDS];
   oid name[MAX_OID_LEN];
   size_t name_length;
   int status;
   int failures = 0;

   SOCK_STARTUP;

   putenv(strdup("POSIXLY_CORRECT=1"));

   /*
    * get the common command line arguments
    */
   switch (arg = snmp_parse_args(argc, argv.get(), &session, "C:", snmpset_optProc)) {
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
      fprintf(stderr, "Missing object name\n");
      snmpset_usage();
      goto out;
   }
   if ((argc - arg) > 3 * SNMP_MAX_CMDLINE_OIDS) {
      fprintf(stderr, "Too many assignments specified. ");
      fprintf(stderr, "Only %d allowed in one request.\n", SNMP_MAX_CMDLINE_OIDS);
      snmpset_usage();
      goto out;
   }

   /*
    * get object names, types, and values
    */
   for (; arg < argc; arg++) {
      DEBUGMSGTL(("snmp_parse_args", "handling (#%d): %s %s %s\n", arg, argv[arg],
                  arg + 1 < argc ? argv[arg + 1] : "", arg + 2 < argc ? argv[arg + 2] : ""));
      names[current_name++] = argv[arg++];
      if (arg < argc) {
         switch (*argv[arg]) {
            case '=':
            case 'i':
            case 'u':
            case '3':
            case 't':
            case 'a':
            case 'o':
            case 's':
            case 'x':
            case 'd':
            case 'b':
            case 'n': /* undocumented */
#ifdef NETSNMP_WITH_OPAQUE_SPECIAL_TYPES
            case 'I':
            case 'U':
            case 'F':
            case 'D':
#endif /* NETSNMP_WITH_OPAQUE_SPECIAL_TYPES */
               types[current_type++] = *argv[arg++];
               break;
            default:
               fprintf(stderr, "%s: Bad object type: %c\n", argv[arg - 1], *argv[arg]);
               goto out;
         }
      } else {
         fprintf(stderr, "%s: Needs type and value\n", argv[arg - 1]);
         goto out;
      }
      if (arg < argc) {
         values[current_value++] = argv[arg];
      } else {
         fprintf(stderr, "%s: Needs value\n", argv[arg - 2]);
         goto out;
      }
   }

   /*
    * open an SNMP session
    */
   ss = snmp_open(&session);
   if (ss == NULL) {
      /*
       * diagnose snmp_open errors with the input netsnmp_session pointer
       */
      snmp_sess_perror_exception("snmpset", &session);
      goto out;
   }

   /*
    * create PDU for SET request and add object names and values to request
    */
   pdu = snmp_pdu_create(SNMP_MSG_SET);
   for (count = 0; count < current_name; count++) {
      name_length = MAX_OID_LEN;
      if (snmp_parse_oid(names[count], name, &name_length) == NULL) {
         snmp_perror_exception(names[count]);
         failures++;
      } else if (snmp_add_var(pdu, name, name_length, types[count], values[count])) {
         snmp_perror_exception(names[count]);
         failures++;
      }
   }

   if (failures) {
      goto close_session;
   }

   /*
    * do the request
    */
   status = snmp_synch_response(ss, pdu, &response);
   if (status == STAT_SUCCESS) {
      if (response->errstat == SNMP_ERR_NOERROR) {
         if (!quiet) {
            for (vars = response->variables; vars; vars = vars->next_variable) {
               auto str_value = print_variable_to_string(vars->name, vars->name_length, vars);
               return_vector.push_back(str_value);
            }
         }
      } else {
         fprintf(stderr, "Error in packet.\nReason: %s\n", snmp_errstring(response->errstat));
         if (response->errindex != 0) {
            fprintf(stderr, "Failed object: ");
            for (count = 1, vars = response->variables; vars && (count != response->errindex);
                 vars = vars->next_variable, count++);
            if (vars) {
               fprint_objid(stderr, vars->name, vars->name_length);
            }
            fprintf(stderr, "\n");
         }
      }
   } else if (status == STAT_TIMEOUT) {
      std::string err_msg = "Timeout: No Response from " + std::string(session.peername) + ".\n";
      throw TimeoutErrorBase(err_msg);
   } else { /* status == STAT_ERROR */
      snmp_sess_perror_exception("snmpset", ss);
   }

   if (response) {
      snmp_free_pdu(response);
   }

close_session:
   snmp_close(ss);

out:
   netsnmp_cleanup_session(&session);
   SOCK_CLEANUP;
   return parse_results(return_vector);
}