/* straight copy from https://github.com/net-snmp/net-snmp/tree/master/apps */
/*
 * snmptable.c - walk a table and print it nicely
 *
 * Update: 1999-10-26 <rs-snmp@revelstone.com>
 * Added ability to use MIB to query tables with non-sequential column OIDs
 * Added code to handle sparse tables
 *
 * Update: 1998-07-17 <jhy@gsu.edu>
 * Added text <special options> to usage().
 */
/**********************************************************************
        Copyright 1997 Niels Baggesen

                      All Rights Reserved

Permission to use, copy, modify, and distribute this software and its
documentation for any purpose and without fee is hereby granted,
provided that the above copyright notice appear in all copies.

I DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN NO EVENT SHALL
I BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
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

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
#include <mutex>
#include <sstream>
#include <string>
#include <vector>

#include "exceptionsbase.h"
#include "helpers.h"
#include "snmptable.h"
#include "thread_safety.h"

namespace {

struct TableColumn {
   int width = 0;
   oid subid = 0;
   std::string label;
   std::string fmt;
};

struct TableContext {
   std::vector<TableColumn> columns;
   std::vector<std::string> data;
   std::vector<bool> has_data;
   std::vector<std::string> indices;
   int index_width = static_cast<int>(sizeof("index ") - 1);
   int entries = 0;
   int end_of_table = 1;
   int headers_only = 0;
   int no_headers = 0;
   int max_width = 0;
   int column_width = 0;
   int brief = 0;
   int show_index = 0;
   char const *left_justify_flag = "";
   char const *field_separator = nullptr;
   std::string table_name;
   oid name[MAX_OID_LEN]{};
   size_t name_length = 0;
   oid root[MAX_OID_LEN]{};
   size_t rootlen = 0;
   int localdebug = 0;
   int use_getbulk = 1;
   int max_getbulk = 10;
   int extra_columns = 0;
   bool first_pass = true;
   std::string opt_error;
};

thread_local TableContext *g_table_ctx = nullptr;

struct TableCtxGuard {
   explicit TableCtxGuard(TableContext *ctx) { g_table_ctx = ctx; }
   ~TableCtxGuard() { g_table_ctx = nullptr; }
   TableCtxGuard(TableCtxGuard const &) = delete;
   TableCtxGuard &operator=(TableCtxGuard const &) = delete;
};

struct QuickPrintGuard {
   int prev_quick_print = 0;
   int prev_dump_packet = 0;
   bool armed = false;
   QuickPrintGuard() = default;
   ~QuickPrintGuard() {
      if (armed) {
         std::lock_guard<std::mutex> lock(g_netsnmp_setup_mutex);
         netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_QUICK_PRINT,
                                prev_quick_print);
         netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DUMP_PACKET,
                                prev_dump_packet);
      }
   }
   QuickPrintGuard(QuickPrintGuard const &) = delete;
   QuickPrintGuard &operator=(QuickPrintGuard const &) = delete;
};

struct SessionCleanupGuard {
   netsnmp_session *session = nullptr;
   explicit SessionCleanupGuard(netsnmp_session *s) : session(s) {}
   ~SessionCleanupGuard() {
      if (session) {
         netsnmp_cleanup_session(session);
      }
   }
   SessionCleanupGuard(SessionCleanupGuard const &) = delete;
   SessionCleanupGuard &operator=(SessionCleanupGuard const &) = delete;
};

std::string trim_trailing_newlines(std::string s) {
   while (!s.empty() && (s.back() == '\n' || s.back() == '\r')) {
      s.pop_back();
   }
   return s;
}

std::string snmptable_usage_string() {
   std::ostringstream oss;
   oss << "USAGE: snmptable [OPTIONS] AGENT TABLE-OID\n\n"
       << "  -C APPOPTS\t\tSet various application specific behaviours:\n"
       << "\t\t\t  b:       brief field names\n"
       << "\t\t\t  B:       do not use GETBULK requests\n"
       << "\t\t\t  c<NUM>:  print table in columns of <NUM> chars width\n"
       << "\t\t\t  f<STR>:  print table delimited with <STR>\n"
       << "\t\t\t  h:       print only the column headers\n"
       << "\t\t\t  H:       print no column headers\n"
       << "\t\t\t  i:       print index values\n"
       << "\t\t\t  l:       left justify output\n"
       << "\t\t\t  r<NUM>:  for GETBULK: set max-repeaters to <NUM>\n"
       << "\t\t\t           for GETNEXT: retrieve <NUM> entries at a time\n"
       << "\t\t\t  w<NUM>:  print table in parts of <NUM> chars width\n";
   return oss.str();
}

void snmptable_optProc(int argc, char *const *argv, int opt) {
   if (!g_table_ctx) {
      return;
   }
   TableContext &ctx = *g_table_ctx;
   auto set_opt_error = [&ctx](std::string const &msg) {
      if (ctx.opt_error.empty()) {
         ctx.opt_error = msg;
      }
   };

   switch (opt) {
      case 'C':
         while (*optarg) {
            switch (*optarg++) {
               case 'w':
                  if (optind < argc && argv[optind]) {
                     ctx.max_width = std::atoi(argv[optind]);
                     if (ctx.max_width == 0) {
                        set_opt_error("Bad -Cw option: " + std::string(argv[optind]) + "\n" +
                                      snmptable_usage_string());
                     }
                     optind++;
                  } else {
                     set_opt_error("Bad -Cw option: no argument given\n" +
                                   snmptable_usage_string());
                  }
                  break;

               case 'c':
                  if (optind < argc && argv[optind]) {
                     ctx.column_width = std::atoi(argv[optind]);
                     if (ctx.column_width <= 2) {
                        set_opt_error("Bad -Cc option: " + std::string(argv[optind]) + "\n" +
                                      snmptable_usage_string());
                     }
                     // Reduce by one for space at end of column
                     ctx.column_width -= 1;
                     optind++;
                  } else {
                     set_opt_error("Bad -Cc option: no argument given\n" +
                                   snmptable_usage_string());
                  }
                  break;

               case 'l':
                  ctx.left_justify_flag = "-";
                  break;

               case 'f':
                  if (optind < argc && argv[optind]) {
                     ctx.field_separator = argv[optind];
                     optind++;
                  } else {
                     set_opt_error("Bad -Cf option: no argument given\n" +
                                   snmptable_usage_string());
                  }
                  break;

               case 'h':
                  ctx.headers_only = 1;
                  break;

               case 'H':
                  ctx.no_headers = 1;
                  break;

               case 'B':
                  ctx.use_getbulk = 0;
                  break;

               case 'b':
                  ctx.brief = 1;
                  break;

               case 'i':
                  ctx.show_index = 1;
                  break;

               case 'r':
                  if (optind < argc && argv[optind]) {
                     ctx.max_getbulk = std::atoi(argv[optind]);
                     if (ctx.max_getbulk == 0) {
                        set_opt_error("Bad -Cr option: " + std::string(argv[optind]) + "\n" +
                                      snmptable_usage_string());
                     }
                     optind++;
                  } else {
                     set_opt_error("Bad -Cr option: no argument given\n" +
                                   snmptable_usage_string());
                  }
                  break;

               default:
                  set_opt_error("Bad option after -C: " + std::string(1, optarg[-1]) + "\n" +
                                snmptable_usage_string());
                  break;
            }
         }
         break;
   }
}

void append_formatted(std::ostringstream &out, char const *fmt, char const *val) {
   char buf[SPRINT_MAX_LEN];
   int needed = std::snprintf(buf, sizeof(buf), fmt, val);
   if (needed < 0) {
      return;
   }
   if (static_cast<size_t>(needed) < sizeof(buf)) {
      out.write(buf, needed);
   } else {
      std::string large(static_cast<size_t>(needed) + 1, '\0');
      std::snprintf(&large[0], large.size(), fmt, val);
      out.write(large.data(), needed);
   }
}

struct CharBufGuard {
   char **buf_ptr = nullptr;
   ~CharBufGuard() {
      if (buf_ptr && *buf_ptr) {
         std::free(*buf_ptr);
         *buf_ptr = nullptr;
      }
   }
   CharBufGuard(CharBufGuard const &) = delete;
   CharBufGuard &operator=(CharBufGuard const &) = delete;
};

void reverse_fields(TableContext &ctx) { std::reverse(ctx.columns.begin(), ctx.columns.end()); }

void get_field_names(TableContext &ctx, std::ostringstream &out) {
   char *buf = nullptr;
   char *name_p = nullptr;
   size_t buf_len = 0;
   size_t out_len = 0;
#ifndef NETSNMP_DISABLE_MIB_LOADING
   struct tree *tbl = nullptr;
#endif /* NETSNMP_DISABLE_MIB_LOADING */
   int going = 1;

   CharBufGuard buf_guard{&buf};

#ifndef NETSNMP_DISABLE_MIB_LOADING
   tbl = get_tree(ctx.root, ctx.rootlen, get_tree_head());
   if (tbl) {
      tbl = tbl->child_list;
      if (tbl) {
         ctx.root[ctx.rootlen++] = tbl->subid;
         tbl = tbl->child_list;
      } else {
         ctx.root[ctx.rootlen++] = 1;
         going = 0;
      }
   }
#endif /* NETSNMP_DISABLE_MIB_LOADING */

   if (sprint_realloc_objid(reinterpret_cast<u_char **>(&buf), &buf_len, &out_len, 1, ctx.root,
                            ctx.rootlen - 1)) {
      ctx.table_name = buf ? buf : "";
      std::free(buf);
      buf = nullptr;
      buf_len = out_len = 0;
   } else {
      std::free(buf);
      buf = nullptr;
      buf_len = out_len = 0;
      ctx.table_name = "[TRUNCATED]";
   }

   int fields = 0;
   while (going) {
      fields++;
#ifndef NETSNMP_DISABLE_MIB_LOADING
      if (tbl) {
         if (tbl->access == MIB_ACCESS_NOACCESS) {
            fields--;
            tbl = tbl->next_peer;
            if (!tbl) {
               going = 0;
            }
            continue;
         }
         ctx.root[ctx.rootlen] = tbl->subid;
         tbl = tbl->next_peer;
         if (!tbl) {
            going = 0;
         }
      } else {
#endif /* NETSNMP_DISABLE_MIB_LOADING */
         ctx.root[ctx.rootlen] = static_cast<oid>(fields);
#ifndef NETSNMP_DISABLE_MIB_LOADING
      }
#endif /* NETSNMP_DISABLE_MIB_LOADING */

      out_len = 0;
      if (sprint_realloc_objid(reinterpret_cast<u_char **>(&buf), &buf_len, &out_len, 1, ctx.root,
                               ctx.rootlen + 1)) {
         name_p = std::strrchr(buf, '.');
         if (name_p == nullptr) {
            name_p = std::strrchr(buf, ':');
         }
         if (name_p == nullptr) {
            name_p = buf;
         } else {
            name_p++;
         }
      } else {
         break;
      }
      if (ctx.localdebug) {
         out << buf << " " << name_p[0] << "\n";
      }
      if ('0' <= name_p[0] && name_p[0] <= '9') {
         fields--;
         break;
      }
      TableColumn col;
      col.label = name_p;
      col.width = static_cast<int>(std::strlen(name_p));
      col.subid = ctx.root[ctx.rootlen];
      ctx.columns.push_back(std::move(col));
   }

   if (ctx.columns.empty()) {
      throw ParseErrorBase("Was that a table? " + ctx.table_name);
   }

   if (name_p) {
      std::memmove(ctx.name, ctx.root, ctx.rootlen * sizeof(oid));
      ctx.name_length = ctx.rootlen + 1;
   }

   if (ctx.brief && ctx.columns.size() > 1) {
      size_t common = ctx.columns[0].label.size();
      for (size_t field = 1; field < ctx.columns.size(); field++) {
         std::string const &prev = ctx.columns[field - 1].label;
         std::string const &curr = ctx.columns[field].label;
         size_t len = 0;
         while (len < prev.size() && len < curr.size() && prev[len] == curr[len]) {
            len++;
         }
         if (len < common) {
            common = len;
         }
      }
      if (common > 0) {
         for (auto &col : ctx.columns) {
            col.label = col.label.substr(common);
            col.width -= static_cast<int>(common);
         }
      }
   }
}

void print_table(TableContext &ctx, std::ostringstream &out) {
   int const fields = static_cast<int>(ctx.columns.size());
   int first_field = 0;
   int last_field = 0;
   int part = 0;
   char string_buf[SPRINT_MAX_LEN];
   std::string index_fmt;

   if (!ctx.no_headers && !ctx.headers_only && ctx.first_pass) {
      out << "SNMP table: " << ctx.table_name << "\n\n";
   }

   for (int field = 0; field < fields; field++) {
      if (ctx.column_width != 0) {
         std::snprintf(string_buf, sizeof(string_buf), "%%%s%d.%ds", ctx.left_justify_flag,
                       ctx.column_width + 1, ctx.column_width);
      } else if (ctx.field_separator == nullptr) {
         std::snprintf(string_buf, sizeof(string_buf), "%%%s%ds", ctx.left_justify_flag,
                       ctx.columns[field].width + 1);
      } else if (field == 0 && !ctx.show_index) {
         std::snprintf(string_buf, sizeof(string_buf), "%%s");
      } else {
         std::snprintf(string_buf, sizeof(string_buf), "%s%%s", ctx.field_separator);
      }
      ctx.columns[field].fmt = string_buf;
   }

   if (ctx.show_index) {
      if (ctx.column_width) {
         std::snprintf(string_buf, sizeof(string_buf), "\nindex: %%s\n");
      } else if (ctx.field_separator == nullptr) {
         std::snprintf(string_buf, sizeof(string_buf), "%%%s%ds", ctx.left_justify_flag,
                       ctx.index_width);
      } else {
         std::snprintf(string_buf, sizeof(string_buf), "%%s");
      }
      index_fmt = string_buf;
   }

   while (last_field != fields) {
      part++;
      if (part != 1 && !ctx.no_headers) {
         out << "\nSNMP table " << ctx.table_name << ", part " << part << "\n\n";
      }
      first_field = last_field;
      int width = 0;
      if (ctx.show_index && !ctx.no_headers && !ctx.column_width && ctx.first_pass) {
         width = ctx.index_width;
         append_formatted(out, index_fmt.c_str(), "index");
      }

      int field = first_field;
      for (; field < fields; field++) {
         if (ctx.max_width) {
            if (ctx.column_width) {
               if (!ctx.no_headers && ctx.first_pass) {
                  width += ctx.column_width + 1;
                  if (field != first_field && width > ctx.max_width) {
                     out << "\n";
                     width = ctx.column_width + 1;
                  }
               }
            } else {
               width += ctx.columns[field].width + 1;
               if (field != first_field && width > ctx.max_width) {
                  break;
               }
            }
         }
         if (!ctx.no_headers && ctx.first_pass) {
            append_formatted(out, ctx.columns[field].fmt.c_str(), ctx.columns[field].label.c_str());
         }
      }
      last_field = field;
      if (!ctx.no_headers && ctx.first_pass) {
         out << "\n";
      }

      for (int entry = 0; entry < ctx.entries; entry++) {
         width = 0;
         if (ctx.show_index) {
            if (!ctx.column_width) {
               width = ctx.index_width;
            }
            append_formatted(out, index_fmt.c_str(), ctx.indices[entry].c_str());
         }
         size_t row_offset = static_cast<size_t>(entry) * static_cast<size_t>(fields);
         for (int f = first_field; f < last_field; f++) {
            if (ctx.column_width && ctx.max_width) {
               width += ctx.column_width + 1;
               if (f != first_field && width > ctx.max_width) {
                  out << "\n";
                  width = ctx.column_width + 1;
               }
            }
            char const *cell =
                ctx.has_data[row_offset + f] ? ctx.data[row_offset + f].c_str() : "?";
            append_formatted(out, ctx.columns[f].fmt.c_str(), cell);
         }
         out << "\n";
      }
   }

   ctx.first_pass = false;
}

char const *extract_index_from_buf(TableContext const &ctx, char *buf) {
   char *name_p = nullptr;
   if (netsnmp_ds_get_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_EXTENDED_INDEX)) {
      name_p = std::strchr(buf, '[');
      return name_p;
   }

   int fmt = netsnmp_ds_get_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_OID_OUTPUT_FORMAT);
   switch (fmt) {
      case NETSNMP_OID_OUTPUT_MODULE:
      case 0:
         name_p = std::strchr(buf, ':');
         if (name_p) {
            name_p++;
         }
         break;
      case NETSNMP_OID_OUTPUT_SUFFIX:
         name_p = buf;
         break;
      case NETSNMP_OID_OUTPUT_FULL:
      case NETSNMP_OID_OUTPUT_NUMERIC:
#ifdef NETSNMP_OID_OUTPUT_FULL_AND_NUMERIC
      case NETSNMP_OID_OUTPUT_FULL_AND_NUMERIC:
#endif
      case NETSNMP_OID_OUTPUT_UCD:
         if (std::strncmp(buf, ctx.table_name.c_str(), ctx.table_name.size()) == 0 &&
             buf[ctx.table_name.size()] != '\0') {
            name_p = buf + ctx.table_name.size() + 1;
            name_p = std::strchr(name_p, '.');
            if (name_p) {
               name_p++;
            }
         } else {
            name_p = nullptr;
         }
         break;
      default:
         throw ParseErrorBase("Unrecognized -O option: " + std::to_string(fmt));
   }

   if (name_p) {
      name_p = std::strchr(name_p, '.');
      if (name_p) {
         name_p++;
      }
   }
   return name_p;
}

std::string format_packet_error(netsnmp_pdu const *response) {
   std::ostringstream err;
   err << "Error in packet.\nReason: " << snmp_errstring(static_cast<int>(response->errstat));
   if (response->errindex != 0) {
      err << "\nFailed object: ";
      long count = 1;
      netsnmp_variable_list *vars = response->variables;
      for (; vars && count != response->errindex; vars = vars->next_variable, count++) {
         /*EMPTY*/
      }
      if (vars) {
         u_char *buf = nullptr;
         size_t buf_len = 0;
         size_t out_len = 0;
         if (sprint_realloc_objid(&buf, &buf_len, &out_len, 1, vars->name, vars->name_length)) {
            err << reinterpret_cast<char const *>(buf);
         }
         std::free(buf);
      }
   }
   return err.str();
}

void get_table_entries(TableContext &ctx,
                       void *ss,
                       netsnmp_session const *sess,
                       std::ostringstream &out) {
   int const fields = static_cast<int>(ctx.columns.size());
   int running = 1;

   while (running && ((ctx.max_width && !ctx.column_width) || (ctx.entries < ctx.max_getbulk))) {
      netsnmp_pdu *pdu = snmp_pdu_create(SNMP_MSG_GETNEXT);
      for (int i = 1; i <= fields; i++) {
         ctx.name[ctx.rootlen] = ctx.columns[i - 1].subid;
         snmp_add_null_var(pdu, ctx.name, ctx.name_length);
      }

      netsnmp_pdu *raw_response = nullptr;
      int status =
          snmp_sess_synch_response(static_cast<struct session_list *>(ss), pdu, &raw_response);
      std::unique_ptr<netsnmp_pdu, SnmpPduDeleter> response(raw_response);

      if (status == STAT_SUCCESS) {
         snmp_check_null_response(response.get());
         if (response->errstat == SNMP_ERR_NOERROR) {
            ctx.entries++;
            ctx.data.resize(static_cast<size_t>(ctx.entries) * static_cast<size_t>(fields));
            ctx.has_data.resize(static_cast<size_t>(ctx.entries) * static_cast<size_t>(fields),
                                false);
            if (ctx.show_index) {
               ctx.indices.resize(static_cast<size_t>(ctx.entries));
            }

            size_t row_offset = static_cast<size_t>(ctx.entries - 1) * static_cast<size_t>(fields);
            int col = -1;
            ctx.end_of_table = 1;
            int have_current_index = 0;
            ctx.name_length = ctx.rootlen + 1;

            char *buf = nullptr;
            size_t out_len = 0;
            size_t buf_len = 0;
            CharBufGuard buf_guard{&buf};

            for (netsnmp_variable_list *vars = response->variables; vars && col + 1 < fields;
                 vars = vars->next_variable) {
               col++;
               ctx.name[ctx.rootlen] = ctx.columns[col].subid;
               if ((vars->name_length < ctx.name_length) ||
                   (vars->name[ctx.rootlen] != ctx.columns[col].subid) ||
                   std::memcmp(ctx.name, vars->name, ctx.name_length * sizeof(oid)) != 0 ||
                   vars->type == SNMP_ENDOFMIBVIEW) {
                  continue;
               }

               if (!have_current_index) {
                  ctx.end_of_table = 0;
                  have_current_index = 1;
                  ctx.name_length = vars->name_length;
                  std::memcpy(ctx.name, vars->name, ctx.name_length * sizeof(oid));
                  out_len = 0;
                  {
                     std::lock_guard<std::mutex> lock(g_netsnmp_mib_mutex);
                     if (!sprint_realloc_objid(reinterpret_cast<u_char **>(&buf), &buf_len,
                                               &out_len, 1, vars->name, vars->name_length)) {
                        break;
                     }
                  }
                  if (ctx.localdebug || ctx.show_index) {
                     char const *name_p = extract_index_from_buf(ctx, buf);
                     if (name_p == nullptr) {
                        running = 0;
                        break;
                     }
                     if (ctx.localdebug) {
                        out << "Name: " << buf << " Index: " << name_p << "\n";
                     }
                     if (ctx.show_index) {
                        ctx.indices[ctx.entries - 1] = name_p;
                        int idx_len = static_cast<int>(std::strlen(name_p));
                        if (idx_len > ctx.index_width) {
                           ctx.index_width = idx_len;
                        }
                     }
                  }
               }

               if (ctx.has_data[row_offset + col]) {
                  throw PacketErrorBase("OID not increasing: " + std::string(buf ? buf : ""));
               }

               out_len = 0;
               {
                  std::lock_guard<std::mutex> lock(g_netsnmp_mib_mutex);
                  sprint_realloc_value(reinterpret_cast<u_char **>(&buf), &buf_len, &out_len, 1,
                                       vars->name, vars->name_length, vars);
               }
               if (buf) {
                  for (char *cp = buf; *cp; cp++) {
                     if (*cp == '\n') {
                        *cp = ' ';
                     }
                  }
                  ctx.data[row_offset + col].assign(buf, out_len);
               } else {
                  ctx.data[row_offset + col].clear();
               }
               ctx.has_data[row_offset + col] = true;
               if (static_cast<int>(out_len) > ctx.columns[col].width) {
                  ctx.columns[col].width = static_cast<int>(out_len);
               }
            }

            if (ctx.end_of_table) {
               --ctx.entries;
               ctx.data.resize(static_cast<size_t>(ctx.entries) * static_cast<size_t>(fields));
               ctx.has_data.resize(static_cast<size_t>(ctx.entries) * static_cast<size_t>(fields));
               if (ctx.show_index) {
                  ctx.indices.resize(static_cast<size_t>(ctx.entries));
               }
               running = 0;
               continue;
            }
         } else {
            running = 0;
            if (response->errstat == SNMP_ERR_NOSUCHNAME) {
               out << "End of MIB\n";
               ctx.end_of_table = 1;
            } else {
               std::lock_guard<std::mutex> lock(g_netsnmp_mib_mutex);
               throw PacketErrorBase(format_packet_error(response.get()));
            }
         }
      } else if (status == STAT_TIMEOUT) {
         throw TimeoutErrorBase("Timeout: No Response from " +
                                std::string(sess && sess->peername ? sess->peername : ""));
      } else {
         snmp_single_sess_perror_exception("snmptable", ss);
      }
   }
}

void getbulk_table_entries(TableContext &ctx,
                           void *ss,
                           netsnmp_session const *sess,
                           std::ostringstream &out) {
   int const fields = static_cast<int>(ctx.columns.size());
   int running = 1;

   while (running) {
      netsnmp_pdu *pdu = snmp_pdu_create(SNMP_MSG_GETBULK);
      pdu->non_repeaters = 0;
      pdu->max_repetitions = ctx.max_getbulk;
      snmp_add_null_var(pdu, ctx.name, ctx.name_length);

      netsnmp_pdu *raw_response = nullptr;
      int status =
          snmp_sess_synch_response(static_cast<struct session_list *>(ss), pdu, &raw_response);
      std::unique_ptr<netsnmp_pdu, SnmpPduDeleter> response(raw_response);

      if (status == STAT_SUCCESS) {
         snmp_check_null_response(response.get());
         if (response->errstat == SNMP_ERR_NOERROR) {
            netsnmp_variable_list *vars = response->variables;
            netsnmp_variable_list *last_var = nullptr;

            char *buf = nullptr;
            size_t buf_len = 0;
            size_t out_len = 0;
            CharBufGuard buf_guard{&buf};

            while (vars) {
               out_len = 0;
               {
                  std::lock_guard<std::mutex> lock(g_netsnmp_mib_mutex);
                  sprint_realloc_objid(reinterpret_cast<u_char **>(&buf), &buf_len, &out_len, 1,
                                       vars->name, vars->name_length);
               }

               if (vars->type == SNMP_ENDOFMIBVIEW || vars->name_length < ctx.rootlen + 1 ||
                   std::memcmp(vars->name, ctx.name, ctx.rootlen * sizeof(oid)) != 0) {
                  running = 0;
                  break;
               }

               int col = 0;
               for (; col < fields; col++) {
                  if (ctx.columns[col].subid == vars->name[ctx.rootlen]) {
                     break;
                  }
               }
               if (col == fields) {
                  ctx.extra_columns = 1;
                  last_var = vars;
                  vars = vars->next_variable;
                  continue;
               }

               char const *name_p = extract_index_from_buf(ctx, buf);
               if (name_p == nullptr) {
                  running = 0;
                  break;
               }

               int row = 0;
               for (; row < ctx.entries; row++) {
                  if (ctx.indices[row] == name_p) {
                     break;
                  }
               }
               if (row == ctx.entries) {
                  ctx.entries++;
                  ctx.data.resize(static_cast<size_t>(ctx.entries) * static_cast<size_t>(fields));
                  ctx.has_data.resize(
                      static_cast<size_t>(ctx.entries) * static_cast<size_t>(fields), false);
                  ctx.indices.resize(static_cast<size_t>(ctx.entries));
                  ctx.indices[row] = name_p;
                  int idx_len = static_cast<int>(std::strlen(name_p));
                  if (idx_len > ctx.index_width) {
                     ctx.index_width = idx_len;
                  }
               }

               size_t row_offset = static_cast<size_t>(row) * static_cast<size_t>(fields);
               if (ctx.has_data[row_offset + col]) {
                  throw PacketErrorBase("OID not increasing: " + std::string(buf ? buf : ""));
               }

               out_len = 0;
               {
                  std::lock_guard<std::mutex> lock(g_netsnmp_mib_mutex);
                  sprint_realloc_value(reinterpret_cast<u_char **>(&buf), &buf_len, &out_len, 1,
                                       vars->name, vars->name_length, vars);
               }
               if (buf) {
                  for (char *cp = buf; *cp; cp++) {
                     if (*cp == '\n') {
                        *cp = ' ';
                     }
                  }
                  ctx.data[row_offset + col].assign(buf, out_len);
               } else {
                  ctx.data[row_offset + col].clear();
               }
               ctx.has_data[row_offset + col] = true;
               if (static_cast<int>(out_len) > ctx.columns[col].width) {
                  ctx.columns[col].width = static_cast<int>(out_len);
               }

               last_var = vars;
               vars = vars->next_variable;
            }

            if (last_var) {
               ctx.name_length = last_var->name_length;
               std::memcpy(ctx.name, last_var->name, ctx.name_length * sizeof(oid));
            }
         } else {
            running = 0;
            if (response->errstat == SNMP_ERR_NOSUCHNAME) {
               out << "End of MIB\n";
            } else {
               std::lock_guard<std::mutex> lock(g_netsnmp_mib_mutex);
               throw PacketErrorBase(format_packet_error(response.get()));
            }
         }
      } else if (status == STAT_TIMEOUT) {
         throw TimeoutErrorBase("Timeout: No Response from " +
                                std::string(sess && sess->peername ? sess->peername : ""));
      } else {
         snmp_single_sess_perror_exception("snmptable", ss);
      }
   }
}

} // namespace

std::vector<std::string> snmptable(std::vector<std::string> const &args,
                                   std::string const &init_app_name) {
   netsnmp_thread_init(init_app_name);

   int argc = 0;
   std::unique_ptr<char *[], Deleter> argv = create_argv(args, argc);

   TableContext ctx;
   TableCtxGuard ctx_guard(&ctx);

   netsnmp_session session;
   std::unique_ptr<void, SnmpSingleSessionCloser> ss;
   std::ostringstream out;
   int arg = 0;
   int total_entries = 0;

   SOCK_STARTUP;
   SockCleanupGuard sock_cleanup_guard;
   QuickPrintGuard quick_print_guard;

   {
      std::lock_guard<std::mutex> setup_lock(g_netsnmp_setup_mutex);

      quick_print_guard.prev_quick_print =
          netsnmp_ds_get_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_QUICK_PRINT);
      quick_print_guard.prev_dump_packet =
          netsnmp_ds_get_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DUMP_PACKET);
      quick_print_guard.armed = true;
      netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_QUICK_PRINT, 1);
      netsnmp_ds_set_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DUMP_PACKET, 0);

      netsnmp_register_loghandler(NETSNMP_LOGHANDLER_NONE, 0);
      netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_MIB_WARNINGS, 0);

#ifdef __GLIBC__
      // Reset GNU getopt internal state before snmp_parse_args, because prior
      // invocations (e.g., -h/-V/-H) may exit early before getopt returns -1.
      optind = 0;
#endif
      arg = snmp_parse_args(argc, argv.get(), &session, "C:", snmptable_optProc);
      if (!ctx.opt_error.empty()) {
         throw ParseErrorBase(ctx.opt_error);
      }

      switch (arg) {
         case NETSNMP_PARSE_ARGS_ERROR:
            throw ParseErrorBase("NETSNMP_PARSE_ARGS_ERROR");

         case NETSNMP_PARSE_ARGS_SUCCESS_EXIT:
            throw ParseErrorBase("NETSNMP_PARSE_ARGS_SUCCESS_EXIT");

         case NETSNMP_PARSE_ARGS_ERROR_USAGE:
            throw ParseErrorBase("NETSNMP_PARSE_ARGS_ERROR_USAGE\n" + snmptable_usage_string());

         default:
            break;
      }

      ctx.localdebug = netsnmp_ds_get_boolean(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_DUMP_PACKET);
   }

   SessionCleanupGuard session_cleanup_guard(&session);

   if (arg + 1 != argc) {
      throw ParseErrorBase("Must have exactly one table name\n" + snmptable_usage_string());
   }

   ctx.rootlen = MAX_OID_LEN;
   {
      std::lock_guard<std::mutex> lock(g_netsnmp_mib_mutex);
      if (!snmp_parse_oid(argv[arg], ctx.root, &ctx.rootlen)) {
         snmp_perror_exception(argv[arg]);
      }
      get_field_names(ctx, out);
      reverse_fields(ctx);
   }

   ss.reset(snmp_sess_open(&session));
   if (!ss) {
      snmp_sess_perror_exception("snmptable", &session);
   }

   netsnmp_session *sess = snmp_sess_session(static_cast<struct session_list *>(ss.get()));
#ifndef NETSNMP_DISABLE_SNMPV1
   if (sess && sess->version == SNMP_VERSION_1) {
      ctx.use_getbulk = 0;
   }
#endif

   do {
      ctx.entries = 0;
      ctx.data.clear();
      ctx.has_data.clear();
      ctx.indices.clear();

      if (!ctx.headers_only) {
         if (ctx.use_getbulk) {
            getbulk_table_entries(ctx, ss.get(), sess, out);
         } else {
            get_table_entries(ctx, ss.get(), sess, out);
         }
      }

      if (ctx.entries || ctx.headers_only) {
         print_table(ctx, out);
      }

      total_entries += ctx.entries;
   } while (!ctx.end_of_table);

   if (total_entries == 0) {
      out << ctx.table_name << ": No entries\n";
   }
   if (ctx.extra_columns) {
      out << ctx.table_name << ": WARNING: More columns on agent than in MIB\n";
   }

   std::string result = trim_trailing_newlines(out.str());
   if (result.empty()) {
      return {};
   }
   return {result};
}
