/* straight copy from https://github.com/net-snmp/net-snmp/tree/master/apps */
/*
 * snmpdf.c - display disk space usage on a network entity via SNMP.
 *
 */

/* Portions of this file are subject to the following copyright(s).  See
 * the Net-SNMP's COPYING file for more details and other copyrights
 * that may apply:
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
/*
 * Portions of this file are copyrighted by:
 * Copyright © 2003 Sun Microsystems, Inc. All rights reserved.
 * Use is subject to license terms specified in the COPYING file
 * distributed with the Net-SNMP package.
 */
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

#include <cstdio>
#include <cstring>
#include <memory>
#include <mutex>
#include <string>
#include <vector>

#include "exceptionsbase.h"
#include "helpers.h"
#include "snmpdf.h"
#include "thread_safety.h"

namespace {

thread_local int g_ucd_mib = 0;
thread_local int g_human_units = 0;
thread_local std::string g_opt_error;

void snmpdf_optProc(int, char *const *, int opt) {
   switch (opt) {
      case 'C':
         while (*optarg) {
            switch (*optarg++) {
               case 'u':
                  g_ucd_mib = 1;
                  break;
               case 'h':
                  g_human_units = 1024;
                  break;
               case 'H':
                  g_human_units = 1000;
                  break;
               default:
                  if (g_opt_error.empty()) {
                     g_opt_error =
                         "Unknown flag passed to -C: " + std::string(1, optarg[-1]) + "\n";
                  }
                  break;
            }
         }
         break;
   }
}

struct SnmpVarbindDeleter {
   void operator()(netsnmp_variable_list *vl) const {
      if (vl) {
         snmp_free_varbind(vl);
      }
   }
};

struct SnmpdfLibraryCleanupGuard {
   ~SnmpdfLibraryCleanupGuard() {
      clear_net_snmp_library_data();
      SOCK_CLEANUP;
   }
};

struct SnmpdfSessionCleanupGuard {
   netsnmp_session *session = nullptr;
   ~SnmpdfSessionCleanupGuard() {
      if (session) {
         netsnmp_cleanup_session(session);
      }
   }
};

int add(netsnmp_pdu *pdu, char const *mibnodename, oid *index, size_t indexlen) {
   oid base[MAX_OID_LEN];
   size_t base_length = MAX_OID_LEN;

   std::memset(base, 0, MAX_OID_LEN * sizeof(oid));

   {
      std::lock_guard<std::mutex> lock(g_netsnmp_mib_mutex);
      if (!snmp_parse_oid(mibnodename, base, &base_length)) {
         snmp_perror_exception(mibnodename);
      }
   }

   if (base_length + indexlen > sizeof(base) / sizeof(base[0])) {
      throw GenericErrorBase("internal error for " + std::string(mibnodename) + ", giving up\n");
   }

   if (index && indexlen) {
      std::memcpy(&(base[base_length]), index, indexlen * sizeof(oid));
      base_length += indexlen;
   }
   DEBUGMSGTL(("add", "created: "));
   DEBUGMSGOID(("add", base, base_length));
   DEBUGMSG(("add", "\n"));
   snmp_add_null_var(pdu, base, base_length);

   return static_cast<int>(base_length);
}

netsnmp_variable_list *collect(
    void *sessp, char const *peername, netsnmp_pdu *pdu, oid *base, size_t base_length) {
   int running = 1;
   netsnmp_variable_list *saved = nullptr;
   netsnmp_variable_list **vlpp = &saved;
   struct VarbindListGuard {
      netsnmp_variable_list *&head;
      bool released = false;
      ~VarbindListGuard() {
         if (!released && head) {
            snmp_free_varbind(head);
         }
      }
   } saved_guard{saved};

   std::unique_ptr<netsnmp_pdu, SnmpPduDeleter> pdu_guard(pdu);

   while (running) {
      netsnmp_pdu *response_raw = nullptr;
      int status = snmp_sess_synch_response(static_cast<struct session_list *>(sessp),
                                            pdu_guard.release(), &response_raw);
      std::unique_ptr<netsnmp_pdu, SnmpPduDeleter> response(response_raw);
      if (status == STAT_TIMEOUT) {
         throw TimeoutErrorBase("Timeout: No Response from " +
                                std::string(peername ? peername : "") + ".\n");
      }
      if (status != STAT_SUCCESS) {
         snmp_single_sess_perror_exception("snmpdf", sessp);
      }
      snmp_check_null_response(response.get());
      if (response->errstat != SNMP_ERR_NOERROR) {
         throw PacketErrorBase(
             "snmpdf: Error in packet: " + std::string(snmp_errstring(response->errstat)) + "\n");
      }
      if (!response->variables || response->variables->name_length <= base_length ||
          snmp_oid_compare(response->variables->name, base_length, base, base_length) != 0) {
         running = 0;
      } else if (response->variables->type == SNMP_NOSUCHINSTANCE ||
                 response->variables->type == SNMP_NOSUCHOBJECT ||
                 response->variables->type == SNMP_ENDOFMIBVIEW) {
         running = 0;
      } else {
         /*
          * get response
          */
         *vlpp = response->variables;
         (*vlpp)->next_variable = nullptr; /* shouldn't be any, but just in case */

         /*
          * create the next request
          */
         pdu_guard.reset(snmp_pdu_create(SNMP_MSG_GETNEXT));
         snmp_add_null_var(pdu_guard.get(), (*vlpp)->name, (*vlpp)->name_length);

         /*
          * finish loop setup
          */
         vlpp = &((*vlpp)->next_variable);
         response->variables = nullptr; /* ahh, forget about it */
      }
   }
   saved_guard.released = true;
   return saved;
}

char *format_human(char *buf, size_t len, unsigned long mem, unsigned long scale) {
   if (mem >= scale * scale * scale * scale) {
      std::snprintf(buf, len, "%4.2fP%sB",
                    static_cast<double>(mem) / (scale * scale * scale * scale),
                    scale == 1024 ? "i" : "");
   } else if (mem >= scale * scale * scale) {
      std::snprintf(buf, len, "%4.2fT%sB", static_cast<double>(mem) / (scale * scale * scale),
                    scale == 1024 ? "i" : "");
   } else if (mem >= scale * scale) {
      std::snprintf(buf, len, "%4.2fG%sB", static_cast<double>(mem) / (scale * scale),
                    scale == 1024 ? "i" : "");
   } else if (mem >= scale) {
      std::snprintf(buf, len, "%4.2fM%sB", static_cast<double>(mem) / scale,
                    scale == 1024 ? "i" : "");
   } else {
      std::snprintf(buf, len, "%4.2fkB", static_cast<double>(mem));
   }
   return buf;
}

/* Computes value*units/divisor in an overflow-proof way.
 */
unsigned long convert_units(unsigned long value, size_t units, size_t divisor) {
   return static_cast<unsigned long>(static_cast<double>(value) * units /
                                     static_cast<double>(divisor));
}

} // namespace

std::vector<std::string> snmpdf(std::vector<std::string> const &args,
                                std::string const &init_app_name) {
   netsnmp_thread_init(init_app_name);
   SOCK_STARTUP;
   SnmpdfLibraryCleanupGuard lib_guard;

   int argc = 0;
   std::unique_ptr<char *[], Deleter> argv = create_argv(args, argc);
   std::vector<std::string> return_vector;

   netsnmp_session session;
   SnmpdfSessionCleanupGuard sess_cleanup_guard;
   std::unique_ptr<void, SnmpSingleSessionCloser> ss;

   int arg = 0;
   oid base[MAX_OID_LEN];
   size_t base_length = 0;
   int count = 0;
   int ucd_mib = 0;
   int human_units = 0;

   {
      std::lock_guard<std::mutex> setup_lock(g_netsnmp_setup_mutex);
      g_ucd_mib = 0;
      g_human_units = 0;
      g_opt_error.clear();
#if defined(__APPLE__) || defined(__FreeBSD__) || defined(__OpenBSD__) || defined(__NetBSD__)
      optreset = 1;
      optind = 1;
#else
      optind = 0;
#endif
      netsnmp_register_loghandler(NETSNMP_LOGHANDLER_NONE, 0);
      netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_MIB_WARNINGS, 0);

      arg = snmp_parse_args(argc, argv.get(), &session, "C:", snmpdf_optProc);
      if (!g_opt_error.empty()) {
         throw ParseErrorBase(g_opt_error);
      }
      switch (arg) {
         case NETSNMP_PARSE_ARGS_ERROR:
            throw ParseErrorBase("NETSNMP_PARSE_ARGS_ERROR");
         case NETSNMP_PARSE_ARGS_SUCCESS_EXIT:
            throw ParseErrorBase("NETSNMP_PARSE_ARGS_SUCCESS_EXIT");
         case NETSNMP_PARSE_ARGS_ERROR_USAGE:
            throw ParseErrorBase("NETSNMP_PARSE_ARGS_ERROR_USAGE");
         default:
            break;
      }
      sess_cleanup_guard.session = &session;
      ucd_mib = g_ucd_mib;
      human_units = g_human_units;
   }

   if (arg != argc) {
      throw ParseErrorBase("snmpdf: extra argument: " + std::string(argv[arg]) + "\n");
   }

   ss.reset(snmp_sess_open(&session));
   if (!ss) {
      snmp_sess_perror_exception("snmpdf", &session);
   }

   char line_buf[SPRINT_MAX_LEN + 256];
   if (human_units) {
      std::snprintf(line_buf, sizeof(line_buf), "%-18s %10s %10s %10s %5s", "Description", "Size",
                    "Used", "Available", "Used%");
   } else {
      std::snprintf(line_buf, sizeof(line_buf), "%-18s %15s %15s %15s %5s", "Description",
                    "Size (kB)", "Used", "Available", "Used%");
   }
   return_vector.emplace_back(line_buf);

   if (ucd_mib == 0) {
      std::unique_ptr<netsnmp_pdu, SnmpPduDeleter> pdu(snmp_pdu_create(SNMP_MSG_GETNEXT));
      base_length = add(pdu.get(), "HOST-RESOURCES-MIB:hrStorageIndex", nullptr, 0);
      std::memcpy(base, pdu->variables->name, base_length * sizeof(oid));

      std::unique_ptr<netsnmp_variable_list, SnmpVarbindDeleter> saved(
          collect(ss.get(), session.peername, pdu.release(), base, base_length));
      netsnmp_variable_list *vlp = saved.get();

      while (vlp) {
         size_t units = 0;
         unsigned long hssize = 0;
         unsigned long hsused = 0;
         char descr[SPRINT_MAX_LEN];
         int len = 0;

         std::unique_ptr<netsnmp_pdu, SnmpPduDeleter> get_pdu(snmp_pdu_create(SNMP_MSG_GET));

         add(get_pdu.get(), "HOST-RESOURCES-MIB:hrStorageDescr", &(vlp->name[base_length]),
             vlp->name_length - base_length);
         add(get_pdu.get(), "HOST-RESOURCES-MIB:hrStorageAllocationUnits",
             &(vlp->name[base_length]), vlp->name_length - base_length);
         add(get_pdu.get(), "HOST-RESOURCES-MIB:hrStorageSize", &(vlp->name[base_length]),
             vlp->name_length - base_length);
         add(get_pdu.get(), "HOST-RESOURCES-MIB:hrStorageUsed", &(vlp->name[base_length]),
             vlp->name_length - base_length);

         netsnmp_pdu *response_raw = nullptr;
         int status = snmp_sess_synch_response(static_cast<struct session_list *>(ss.get()),
                                               get_pdu.release(), &response_raw);
         std::unique_ptr<netsnmp_pdu, SnmpPduDeleter> response(response_raw);
         if (status == STAT_TIMEOUT) {
            throw TimeoutErrorBase("Timeout: No Response from " +
                                   std::string(session.peername ? session.peername : "") + ".\n");
         }
         if (status != STAT_SUCCESS) {
            snmp_single_sess_perror_exception("snmpdf", ss.get());
         }
         snmp_check_null_response(response.get());

         netsnmp_variable_list *vlp2 = response->variables;
         if (!vlp2 || vlp2->type == SNMP_NOSUCHINSTANCE || vlp2->type == SNMP_NOSUCHOBJECT) {
            goto next;
         }
         len = static_cast<int>(vlp2->val_len);
         if (len >= SPRINT_MAX_LEN) {
            len = SPRINT_MAX_LEN - 1;
         }
         if (vlp2->val.string && len > 0) {
            std::memcpy(descr, vlp2->val.string, static_cast<size_t>(len));
         } else {
            len = 0;
         }
         descr[len] = '\0';

         vlp2 = vlp2->next_variable;
         if (!vlp2 || vlp2->type == SNMP_NOSUCHINSTANCE || vlp2->type == SNMP_NOSUCHOBJECT) {
            goto next;
         }
         units = vlp2->val.integer ? static_cast<size_t>(*(vlp2->val.integer)) : 0;

         vlp2 = vlp2->next_variable;
         if (!vlp2 || vlp2->type == SNMP_NOSUCHINSTANCE || vlp2->type == SNMP_NOSUCHOBJECT) {
            goto next;
         }
         hssize = vlp2->val.integer ? static_cast<unsigned long>(*(vlp2->val.integer)) : 0;

         vlp2 = vlp2->next_variable;
         if (!vlp2 || vlp2->type == SNMP_NOSUCHINSTANCE || vlp2->type == SNMP_NOSUCHOBJECT) {
            goto next;
         }
         hsused = vlp2->val.integer ? static_cast<unsigned long>(*(vlp2->val.integer)) : 0;

         if (human_units) {
            char size[32], used[32], avail[32];
            std::snprintf(
                line_buf, sizeof(line_buf), "%-18s %10s %10s %10s %4lu%%", descr,
                format_human(size, sizeof(size),
                             units ? convert_units(hssize, units, 1024) : hssize, human_units),
                format_human(used, sizeof(used),
                             units ? convert_units(hsused, units, 1024) : hsused, human_units),
                format_human(avail, sizeof(avail),
                             units ? convert_units(hssize - hsused, units, 1024) : hssize - hsused,
                             human_units),
                hssize ? convert_units(hsused, 100, hssize) : hsused);
         } else {
            std::snprintf(line_buf, sizeof(line_buf), "%-18s %15lu %15lu %15lu %4lu%%", descr,
                          units ? convert_units(hssize, units, 1024) : hssize,
                          units ? convert_units(hsused, units, 1024) : hsused,
                          units ? convert_units(hssize - hsused, units, 1024) : hssize - hsused,
                          hssize ? convert_units(hsused, 100, hssize) : hsused);
         }
         return_vector.emplace_back(line_buf);

      next:
         vlp = vlp->next_variable;
         count++;
      }
   }

   if (count == 0) {
      std::unique_ptr<netsnmp_pdu, SnmpPduDeleter> pdu(snmp_pdu_create(SNMP_MSG_GETNEXT));
      base_length = add(pdu.get(), "UCD-SNMP-MIB:dskIndex", nullptr, 0);
      std::memcpy(base, pdu->variables->name, base_length * sizeof(oid));

      std::unique_ptr<netsnmp_variable_list, SnmpVarbindDeleter> saved(
          collect(ss.get(), session.peername, pdu.release(), base, base_length));
      netsnmp_variable_list *vlp = saved.get();

      while (vlp) {
         unsigned long hssize = 0;
         unsigned long hsused = 0;
         char descr[SPRINT_MAX_LEN];
         int len = 0;

         std::unique_ptr<netsnmp_pdu, SnmpPduDeleter> get_pdu(snmp_pdu_create(SNMP_MSG_GET));

         add(get_pdu.get(), "UCD-SNMP-MIB:dskPath", &(vlp->name[base_length]),
             vlp->name_length - base_length);
         add(get_pdu.get(), "UCD-SNMP-MIB:dskTotal", &(vlp->name[base_length]),
             vlp->name_length - base_length);
         add(get_pdu.get(), "UCD-SNMP-MIB:dskUsed", &(vlp->name[base_length]),
             vlp->name_length - base_length);

         netsnmp_pdu *response_raw = nullptr;
         int status = snmp_sess_synch_response(static_cast<struct session_list *>(ss.get()),
                                               get_pdu.release(), &response_raw);
         std::unique_ptr<netsnmp_pdu, SnmpPduDeleter> response(response_raw);
         if (status == STAT_TIMEOUT) {
            throw TimeoutErrorBase("Timeout: No Response from " +
                                   std::string(session.peername ? session.peername : "") + ".\n");
         }
         if (status != STAT_SUCCESS) {
            snmp_single_sess_perror_exception("snmpdf", ss.get());
         }
         snmp_check_null_response(response.get());

         netsnmp_variable_list *vlp2 = response->variables;
         if (!vlp2 || vlp2->type == SNMP_NOSUCHINSTANCE || vlp2->type == SNMP_NOSUCHOBJECT) {
            goto next2;
         }
         len = static_cast<int>(vlp2->val_len);
         if (len >= SPRINT_MAX_LEN) {
            len = SPRINT_MAX_LEN - 1;
         }
         if (vlp2->val.string && len > 0) {
            std::memcpy(descr, vlp2->val.string, static_cast<size_t>(len));
         } else {
            len = 0;
         }
         descr[len] = '\0';

         vlp2 = vlp2->next_variable;
         if (!vlp2 || vlp2->type == SNMP_NOSUCHINSTANCE || vlp2->type == SNMP_NOSUCHOBJECT) {
            goto next2;
         }
         hssize = vlp2->val.integer ? static_cast<unsigned long>(*(vlp2->val.integer)) : 0;

         vlp2 = vlp2->next_variable;
         if (!vlp2 || vlp2->type == SNMP_NOSUCHINSTANCE || vlp2->type == SNMP_NOSUCHOBJECT) {
            goto next2;
         }
         hsused = vlp2->val.integer ? static_cast<unsigned long>(*(vlp2->val.integer)) : 0;

         if (human_units) {
            char size[32], used[32], avail[32];
            std::snprintf(line_buf, sizeof(line_buf), "%-18s %10s %10s %10s %4lu%%", descr,
                          format_human(size, sizeof(size), hssize, human_units),
                          format_human(used, sizeof(used), hsused, human_units),
                          format_human(avail, sizeof(avail), hssize - hsused, human_units),
                          hssize ? convert_units(hsused, 100, hssize) : hsused);
         } else {
            std::snprintf(line_buf, sizeof(line_buf), "%-18s %15lu %15lu %15lu %4lu%%", descr,
                          hssize, hsused, hssize - hsused,
                          hssize ? convert_units(hsused, 100, hssize) : hsused);
         }
         return_vector.emplace_back(line_buf);

      next2:
         vlp = vlp->next_variable;
         count++;
      }
   }

   if (count == 0) {
      throw GenericErrorBase("Failed to locate any partitions.\n");
   }

   return return_vector;
} /* end snmpdf() */
