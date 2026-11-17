/* straight copy from https://github.com/net-snmp/net-snmp/tree/master/apps */
/*
 * snmptranslate.c - report or translate info about oid from mibs
 *
 * Update: 1998-07-17 <jhy@gsu.edu>
 * Added support for dumping alternate oid reports (-t and -T options).
 * Added more detailed (useful?) usage info.
 */
/************************************************************************
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
#ifdef HAVE_SYS_SELECT_H
#include <sys/select.h>
#endif
#ifdef HAVE_NETINET_IN_H
#include <netinet/in.h>
#endif
#include <ctype.h>
#include <net-snmp/config_api.h>
#include <net-snmp/mib_api.h>
#include <net-snmp/output_api.h>
#include <net-snmp/utilities.h>
#include <stdio.h>

#include <cstdio>
#include <functional>
#include <memory>
#include <mutex>
#include <sstream>
#include <string>
#include <vector>

#include "exceptionsbase.h"
#include "helpers.h"
#include "snmptranslate.h"
#include "thread_safety.h"

namespace {

std::string trim_trailing_newlines(std::string s) {
   while (!s.empty() && (s.back() == '\n' || s.back() == '\r')) {
      s.pop_back();
   }
   return s;
}

std::string capture_to_string(std::function<void(FILE *)> const &writer) {
   std::unique_ptr<FILE, decltype(&std::fclose)> fp(std::tmpfile(), &std::fclose);
   if (!fp) {
      throw GenericErrorBase("Failed to create temporary file for snmptranslate output");
   }
   writer(fp.get());
   std::fflush(fp.get());
   std::rewind(fp.get());

   std::string result;
   char buf[4096];
   while (true) {
      size_t n = std::fread(buf, 1, sizeof(buf), fp.get());
      if (n > 0) {
         result.append(buf, n);
      }
      if (n < sizeof(buf)) {
         break;
      }
   }
   return trim_trailing_newlines(std::move(result));
}

std::string format_objid_no_newline(oid const *objid, size_t objidlen) {
   u_char *buf = nullptr;
   size_t buf_len = 256;
   size_t out_len = 0;
   int buf_overflow = 0;

   buf = static_cast<u_char *>(std::calloc(buf_len, 1));
   if (!buf) {
      throw GenericErrorBase("Failed to allocate buffer for OID formatting");
   }

   netsnmp_sprint_realloc_objid_tree(&buf, &buf_len, &out_len, 1, &buf_overflow, objid, objidlen);
   std::string out(reinterpret_cast<char const *>(buf));
   if (buf_overflow) {
      out += " [TRUNCATED]";
   }
   SNMP_FREE(buf);
   return out;
}

std::string snmptranslate_usage_string() {
   std::ostringstream oss;
   oss << "USAGE: snmptranslate [OPTIONS] OID [OID]...\n\n"
       << "  Version:  " << netsnmp_get_version() << "\n"
       << "  Web:      http://www.net-snmp.org/\n"
       << "  Email:    net-snmp-coders@lists.sourceforge.net\n\nOPTIONS:\n"
       << "  -h\t\t\tdisplay this help message\n"
       << "  -V\t\t\tdisplay package version number\n"
       << "  -m MIB[" ENV_SEPARATOR "...]\t\tload given list of MIBs (ALL loads everything)\n"
       << "  -M DIR[" ENV_SEPARATOR "...]\t\tlook in given list of directories for MIBs\n"
       << "  -D[TOKEN[,...]]\tturn on debugging output for the specified TOKENs\n"
       << "  -w WIDTH\t\tset width of tree and detail output\n"
       << "  -T TRANSOPTS\t\tSet various options controlling report produced:\n"
       << "\t\t\t  B:  print all matching objects for a regex search\n"
       << "\t\t\t  d:  print full details of the given OID\n"
       << "\t\t\t  p:  print tree format symbol table\n"
       << "\t\t\t  a:  print ASCII format symbol table\n"
       << "\t\t\t  l:  enable labeled OID report\n"
       << "\t\t\t  o:  enable OID report\n"
       << "\t\t\t  s:  enable dotted symbolic report\n"
       << "\t\t\t  z:  enable MIB child OID report\n"
       << "\t\t\t  t:  enable alternate format symbolic suffix report\n";
   return oss.str();
}

struct TranslateDsGuard {
   ~TranslateDsGuard() {
      std::lock_guard<std::mutex> lock(g_netsnmp_mib_mutex);
      netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_RANDOM_ACCESS, 0);
      netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_REGEX_ACCESS, 0);
      netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_SAVE_MIB_DESCRS, 0);
   }
};

int show_all_matched_objects_vec(std::vector<std::string> &out,
                                 char const *patmatch,
                                 oid *name,
                                 size_t *name_length,
                                 int f_desc,
                                 int width) {
   int result = 0;
   int count = 0;
   size_t savlen = *name_length;
#ifndef NETSNMP_DISABLE_MIB_LOADING
   clear_tree_flags(get_tree_head());
#endif /* NETSNMP_DISABLE_MIB_LOADING */

   while (true) {
      *name_length = savlen;
#ifndef NETSNMP_DISABLE_MIB_LOADING
      result = get_wild_node(patmatch, name, name_length);
#endif /* NETSNMP_DISABLE_MIB_LOADING */
      if (!result) {
         break;
      }
      count++;

      std::string entry = format_objid_no_newline(name, *name_length);
#ifndef NETSNMP_DISABLE_MIB_LOADING
      if (f_desc) {
         std::string desc = capture_to_string(
             [&](FILE *fp) { fprint_description(fp, name, *name_length, width); });
         if (!desc.empty()) {
            entry += "\n" + desc;
         }
      }
#else
      (void)f_desc;
      (void)width;
#endif /* NETSNMP_DISABLE_MIB_LOADING */
      out.push_back(std::move(entry));
   }

   return count;
}

} // namespace

std::vector<std::string> snmptranslate(std::vector<std::string> const &args,
                                       std::string const &init_app_name) {
   netsnmp_thread_init(init_app_name);

   int argc = 0;
   std::unique_ptr<char *[], Deleter> argv = create_argv(args, argc);
   std::vector<std::string> return_vector;

   int arg = 0;
   char *current_name = nullptr;
   char const *cp = nullptr;
   oid name[MAX_OID_LEN];
   size_t name_length = 0;
   int description = 0;
   int print = 0;
   int find_all = 0;
   int width = 1000000;

   SOCK_STARTUP;
   SockCleanupGuard sock_cleanup_guard;
   TranslateDsGuard translate_ds_guard;

   std::lock_guard<std::mutex> setup_lock(g_netsnmp_setup_mutex);
   std::lock_guard<std::mutex> mib_lock(g_netsnmp_mib_mutex);

   // Reset getopt global state before parsing arguments.
   optind = 1;
   opterr = 0;
#if defined(__APPLE__) || defined(__FreeBSD__) || defined(__OpenBSD__) || defined(__NetBSD__)
   optreset = 1;
#endif

   while ((arg = getopt(argc, argv.get(), "Vhm:M:w:D:P:T:O:I:L:")) != EOF) {
      switch (arg) {
         case 'h':
            throw ParseErrorBase(snmptranslate_usage_string());

         case 'm':
            setenv("MIBS", optarg, 1);
            if (std::strcmp(optarg, "ALL") == 0) {
               read_all_mibs();
            } else {
               netsnmp_read_module(optarg);
            }
            break;

         case 'M':
            setenv("MIBDIRS", optarg, 1);
            netsnmp_set_mib_directory(optarg);
            break;

         case 'D':
            debug_register_tokens(optarg);
            snmp_set_do_debugging(1);
            break;

         case 'V':
            return {"NET-SNMP version: " + std::string(netsnmp_get_version())};

         case 'w':
            width = std::atoi(optarg);
            if (width <= 0) {
               throw ParseErrorBase("Invalid width specification: " + std::string(optarg));
            }
            break;

#ifndef NETSNMP_DISABLE_MIB_LOADING
         case 'P':
            cp = snmp_mib_toggle_options(optarg);
            if (cp != nullptr) {
               throw ParseErrorBase("Unknown parser option to -P: " + std::string(1, *cp));
            }
            break;
#endif /* NETSNMP_DISABLE_MIB_LOADING */

         case 'O':
            cp = snmp_out_toggle_options(optarg);
            if (cp != nullptr) {
               throw ParseErrorBase("Unknown OID option to -O: " + std::string(1, *cp));
            }
            break;

         case 'I':
            cp = snmp_in_toggle_options(optarg);
            if (cp != nullptr) {
               throw ParseErrorBase("Unknown OID option to -I: " + std::string(1, *cp));
            }
            break;

         case 'T':
            for (cp = optarg; *cp; cp++) {
               switch (*cp) {
#ifndef NETSNMP_DISABLE_MIB_LOADING
                  case 'l':
                     print = 3;
                     print_oid_report_enable_labeledoid();
                     break;
                  case 'o':
                     print = 3;
                     print_oid_report_enable_oid();
                     break;
                  case 's':
                     print = 3;
                     print_oid_report_enable_symbolic();
                     break;
                  case 't':
                     print = 3;
                     print_oid_report_enable_suffix();
                     break;
                  case 'z':
                     print = 3;
                     print_oid_report_enable_mibchildoid();
                     break;
#endif /* NETSNMP_DISABLE_MIB_LOADING */
                  case 'd':
                     description = 1;
                     netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_SAVE_MIB_DESCRS,
                                            1);
                     break;
                  case 'B':
                     find_all = 1;
                     break;
                  case 'p':
                     print = 1;
                     break;
                  case 'a':
                     print = 2;
                     break;
                  default:
                     throw ParseErrorBase("Invalid -T<lostpad> character: " + std::string(1, *cp));
               }
            }
            break;

         case 'L':
            if (snmp_log_options(optarg, argc, argv.get()) < 0) {
               throw ParseErrorBase("Invalid log option: " + std::string(optarg));
            }
            break;

         default:
            throw ParseErrorBase("Invalid option: -" +
                                 std::string(1, static_cast<char>(optopt ? optopt : arg)));
      }
   }

   if (optind < argc) {
      current_name = argv[optind];
   }

   if (current_name == nullptr) {
      switch (print) {
         default:
            throw ParseErrorBase("Missing object name\n" + snmptranslate_usage_string());
#ifndef NETSNMP_DISABLE_MIB_LOADING
         case 1:
            return_vector.push_back(
                capture_to_string([&](FILE *fp) { print_mib_tree(fp, get_tree_head(), width); }));
            break;
         case 2:
            return_vector.push_back(capture_to_string([&](FILE *fp) { print_ascii_dump(fp); }));
            break;
         case 3:
            return_vector.push_back(capture_to_string([&](FILE *fp) { print_oid_report(fp); }));
            break;
#endif /* NETSNMP_DISABLE_MIB_LOADING */
      }
      return return_vector;
   }

   do {
      if (std::strcmp(current_name, "-") == 0 && print == 0) {
         throw ParseErrorBase("Reading from stdin ('-') is not supported in ezsnmp::snmptranslate");
      }

      name_length = MAX_OID_LEN;
      if (netsnmp_ds_get_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_RANDOM_ACCESS)) {
#ifndef NETSNMP_DISABLE_MIB_LOADING
         if (!get_node(current_name, name, &name_length)) {
#endif /* NETSNMP_DISABLE_MIB_LOADING */
            throw UnknownObjectIDErrorBase("Unknown object identifier: " +
                                           std::string(current_name));
#ifndef NETSNMP_DISABLE_MIB_LOADING
         }
#endif /* NETSNMP_DISABLE_MIB_LOADING */
      } else if (find_all) {
         if (0 == show_all_matched_objects_vec(return_vector, current_name, name, &name_length,
                                               description, width)) {
            throw UnknownObjectIDErrorBase("Unable to find a matching object identifier for \"" +
                                           std::string(current_name) + "\"");
         }
         break;
      } else if (netsnmp_ds_get_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_REGEX_ACCESS)) {
#ifndef NETSNMP_DISABLE_MIB_LOADING
         if (0 == get_wild_node(current_name, name, &name_length)) {
#endif /* NETSNMP_DISABLE_MIB_LOADING */
            throw UnknownObjectIDErrorBase("Unable to find a matching object identifier for \"" +
                                           std::string(current_name) + "\"");
#ifndef NETSNMP_DISABLE_MIB_LOADING
         }
#endif /* NETSNMP_DISABLE_MIB_LOADING */
      } else {
         if (!read_objid(current_name, name, &name_length)) {
            snmp_perror_exception(current_name);
         }
      }

      if (print == 1) {
#ifndef NETSNMP_DISABLE_MIB_LOADING
         struct tree *tp = get_tree(name, name_length, get_tree_head());
         if (tp == nullptr) {
#endif /* NETSNMP_DISABLE_MIB_LOADING */
            throw UnknownObjectIDErrorBase("Unable to find a matching object identifier for \"" +
                                           std::string(current_name) + "\"");
#ifndef NETSNMP_DISABLE_MIB_LOADING
         }
         return_vector.push_back(
             capture_to_string([&](FILE *fp) { print_mib_tree(fp, tp, width); }));
#endif /* NETSNMP_DISABLE_MIB_LOADING */
      } else {
         std::string entry = format_objid_no_newline(name, name_length);
         if (description) {
#ifndef NETSNMP_DISABLE_MIB_LOADING
            std::string desc = capture_to_string(
                [&](FILE *fp) { fprint_description(fp, name, name_length, width); });
            if (!desc.empty()) {
               entry += "\n" + desc;
            }
#endif /* NETSNMP_DISABLE_MIB_LOADING */
         }
         return_vector.push_back(std::move(entry));
      }

      current_name = argv[++optind];
   } while (optind < argc);

   return return_vector;
}
