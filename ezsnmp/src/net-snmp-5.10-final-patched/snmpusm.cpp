/* straight copy from https://github.com/net-snmp/net-snmp/tree/master/apps */
/*
 * snmpusm.c - send snmp SET requests to a network entity to change the
 *             usm user database
 *
 * XXX get engineID dynamically.
 * XXX read passwords from prompts
 * XXX customize responses with user names, etc.
 */
/* Portions of this file are subject to the following copyright(s).  See
 * the Net-SNMP's COPYING file for more details and other copyrights
 * that may apply:
 */
/*
 * Portions of this file are copyrighted by:
 * Copyright © 2003 Sun Microsystems, Inc. All rights reserved.
 * Use is subject to license terms specified in the COPYING file
 * distributed with the Net-SNMP package.
 */
#if defined(__has_include)
#if __has_include(<net-snmp/library/openssl_config.h>)
#include <net-snmp/library/openssl_config.h>
#endif
#endif
#include <net-snmp/net-snmp-config.h>
#include <net-snmp/net-snmp-includes.h>
#if defined(__has_include)
#if __has_include(<net-snmp/library/snmp_openssl.h>)
#include <net-snmp/library/snmp_openssl.h>
#endif
#endif
#if defined(HAVE_OPENSSL_DH_H) && defined(HAVE_LIBCRYPTO)
#include <openssl/dh.h>
#endif /* HAVE_OPENSSL_DH_H && HAVE_LIBCRYPTO */

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
# include <sys/time.h>
# include <time.h>
#else
# ifdef HAVE_SYS_TIME_H
#  include <sys/time.h>
# else
#  include <time.h>
# endif
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

#include <iomanip>
#include <memory>
#include <mutex>
#include <sstream>
#include <string>
#include <vector>

#include "exceptionsbase.h"
#include "helpers.h"
#include "snmpusm.h"
#include "thread_safety.h"

#define CMD_PASSWD_NAME    "passwd"
#define CMD_PASSWD         1
#define CMD_CREATE_NAME    "create"
#define CMD_CREATE         2
#define CMD_DELETE_NAME    "delete"
#define CMD_DELETE         3
#define CMD_CLONEFROM_NAME "cloneFrom"
#define CMD_CLONEFROM      4
#define CMD_ACTIVATE_NAME  "activate"
#define CMD_ACTIVATE       5
#define CMD_DEACTIVATE_NAME "deactivate"
#define CMD_DEACTIVATE     6
#define CMD_CHANGEKEY_NAME  "changekey"
#define CMD_CHANGEKEY      7

#define CMD_NUM    7

static char const *successNotes[CMD_NUM] = {
    "SNMPv3 Key(s) successfully changed.", "User successfully created.",
    "User successfully deleted.",          "User successfully cloned.",
    "User successfully activated.",        "User successfully deactivated.",
    "SNMPv3 Key(s) successfully changed.",
};

#define                   USM_OID_LEN    12
#define                DH_USM_OID_LEN    11

#if defined(HAVE_OPENSSL_DH_H) && defined(HAVE_LIBCRYPTO)
static oid usmDHParameters[] = { 1,3,6,1,3,101,1,1,1,0 };
static size_t usmDHParameters_len = OID_LENGTH(usmDHParameters);
#endif /* HAVE_OPENSSL_DH_H && HAVE_LIBCRYPTO */

namespace {

thread_local int doauthkey = 0;
thread_local int doprivkey = 0;
thread_local int uselocalizedkey = 0;
thread_local size_t usmUserEngineIDLen = 0;
thread_local u_char *usmUserEngineID = nullptr;
thread_local bool usmUserEngineID_allocated = false;
thread_local char const *usmUserPublic_val = nullptr;
thread_local int docreateandwait = 0;

struct SnmpusmStateGuard {
   SnmpusmStateGuard() { reset(); }
   ~SnmpusmStateGuard() { reset(); }

   SnmpusmStateGuard(SnmpusmStateGuard const &) = delete;
   SnmpusmStateGuard &operator=(SnmpusmStateGuard const &) = delete;

   static void reset() {
      doauthkey = 0;
      doprivkey = 0;
      uselocalizedkey = 0;
      docreateandwait = 0;
      usmUserPublic_val = nullptr;
      if (usmUserEngineID_allocated && usmUserEngineID != nullptr) {
         free(usmUserEngineID);
}
      usmUserEngineID = nullptr;
      usmUserEngineIDLen = 0;
      usmUserEngineID_allocated = false;
   }
};

struct NetsnmpSessionCleanupGuard {
   netsnmp_session *session = nullptr;
   ~NetsnmpSessionCleanupGuard() {
      if (session != nullptr) {
         netsnmp_cleanup_session(session);
      }
   }
};

/*
 * setup_oid appends to the oid the index for the engineid/user 
 */
void setup_oid(oid *it, size_t *len, u_char *id, size_t idlen, char const *user) {
   size_t itIndex = *len;
   size_t user_len = strlen(user);

   if (itIndex + 1 + idlen + 1 + user_len > MAX_OID_LEN) {
      throw GenericErrorBase("OID length exceeds MAX_OID_LEN\n");
    }

   *len = itIndex + 1 + idlen + 1 + user_len;

    it[itIndex++] = idlen;
   for (size_t i = 0; i < idlen; i++) {
        it[itIndex++] = id[i];
    }

   it[itIndex++] = user_len;
   for (size_t i = 0; i < user_len; i++) {
      it[itIndex++] = static_cast<unsigned char>(user[i]);
    }
}

#if defined(HAVE_OPENSSL_DH_H) && defined(HAVE_LIBCRYPTO)
int get_USM_DH_key(netsnmp_variable_list *vars,
                   netsnmp_variable_list *dhvar,
               size_t outkey_len,
                   netsnmp_pdu *pdu,
                   char const *keyname,
                   oid *keyoid,
                   size_t keyoid_len,
                   std::vector<std::string> &output) {
    u_char *dhkeychange;
    DH *dh;
   BIGNUM const *p, *g, *pub_key;
    BIGNUM *other_pub;
    u_char *key;
    size_t key_len;

   if (!vars || !vars->val.string || !dhvar || !dhvar->val.string) {
        return SNMPERR_GENERR;
   }
            
   dhkeychange = static_cast<u_char *>(malloc(2 * vars->val_len * sizeof(char)));
   if (!dhkeychange) {
        return SNMPERR_GENERR;
   }
    
    memcpy(dhkeychange, vars->val.string, vars->val_len);

    {
      unsigned char const *cp = dhvar->val.string;
        dh = d2i_DHparams(NULL, &cp, dhvar->val_len);
    }

   if (dh) {
        DH_get0_pqg(dh, &p, NULL, &g);
   }

    if (!dh || !g || !p) {
        DH_free(dh);
        SNMP_FREE(dhkeychange);
        return SNMPERR_GENERR;
    }

    if (!DH_generate_key(dh)) {
        DH_free(dh);
        SNMP_FREE(dhkeychange);
        return SNMPERR_GENERR;
    }

    DH_get0_key(dh, &pub_key, NULL);
   if (vars->val_len != static_cast<unsigned int>(BN_num_bytes(pub_key))) {
      int pub_bytes = BN_num_bytes(pub_key);
      unsigned long val_len = static_cast<unsigned long>(vars->val_len);
        DH_free(dh);
        SNMP_FREE(dhkeychange);
      throw GenericErrorBase("incorrect diffie-helman lengths (" + std::to_string(val_len) +
                             " != " + std::to_string(pub_bytes) + ")\n");
    }

    BN_bn2bin(pub_key, dhkeychange + vars->val_len);

    key_len = DH_size(dh);
    if (!key_len || key_len < outkey_len) {
        DH_free(dh);
        SNMP_FREE(dhkeychange);
        return SNMPERR_GENERR;
    }
   key = static_cast<u_char *>(malloc(key_len * sizeof(u_char)));

    if (!key) {
        DH_free(dh);
        SNMP_FREE(dhkeychange);
        return SNMPERR_GENERR;
    }

    other_pub = BN_bin2bn(vars->val.string, vars->val_len, NULL);
    if (!other_pub) {
        DH_free(dh);
        SNMP_FREE(dhkeychange);
        SNMP_FREE(key);
        return SNMPERR_GENERR;
    }

    {
        int computed_len = DH_compute_key(key, other_pub, dh);
        u_char *kp;

      if (computed_len < static_cast<int>(outkey_len)) {
            DH_free(dh);
            SNMP_FREE(dhkeychange);
            BN_free(other_pub);
            SNMP_FREE(key);
            return SNMPERR_GENERR;
        }
      std::ostringstream oss;
      oss << "new " << keyname << " key: 0x" << std::hex << std::setfill('0');
      for (kp = key + computed_len - outkey_len; kp - key < computed_len; kp++) {
         oss << std::setw(2) << static_cast<unsigned int>(*kp);
        }
      output.push_back(oss.str());
    }

   snmp_pdu_add_variable(pdu, keyoid, keyoid_len, ASN_OCTET_STR, dhkeychange, 2 * vars->val_len);

    DH_free(dh);
    SNMP_FREE(dhkeychange);
    BN_free(other_pub);
    SNMP_FREE(key);

    return SNMPERR_SUCCESS;
}
#endif /* HAVE_OPENSSL_DH_H && HAVE_LIBCRYPTO */

} // namespace

void snmpusm_usage(void) {
   fprintf(stderr, "Usage: snmpusm ");
   snmp_parse_args_usage(stderr);
   fprintf(stderr, " COMMAND\n\n");
   snmp_parse_args_descriptions(stderr);
   fprintf(stderr, "\nsnmpusm commands:\n");
   fprintf(stderr, "  [options]               create     USER [CLONEFROM-USER]\n");
   fprintf(stderr, "  [options]               delete     USER\n");
   fprintf(stderr, "  [options]               activate   USER\n");
   fprintf(stderr, "  [options]               deactivate USER\n");
   fprintf(stderr, "  [options] [-Cw]         cloneFrom  USER CLONEFROM-USER\n");
   fprintf(stderr, "  [options] [-Ca] [-Cx]   changekey  [USER]\n");
   fprintf(stderr, "  [options] [-Ca] [-Cx]   passwd     OLD-PASSPHRASE NEW-PASSPHRASE [USER]\n");
   fprintf(stderr, "  [options] (-Ca|-Cx) -Ck passwd     OLD-KEY-OR-PASS NEW-KEY-OR-PASS [USER]\n");
   fprintf(stderr, "\nsnmpusm options:\n");
   fprintf(stderr, "\t-CE ENGINE-ID\tSet usmUserEngineID (e.g. 800000020109840301).\n");
   fprintf(stderr, "\t-Cp STRING\tSet usmUserPublic value to STRING.\n");
   fprintf(stderr, "\t-Cw\t\tCreate the user with createAndWait.\n");
   fprintf(stderr, "\t\t\t(it won't be active until you activate it)\n");
   fprintf(stderr, "\t-Cx\t\tChange the privacy key.\n");
   fprintf(stderr, "\t-Ca\t\tChange the authentication key.\n");
   fprintf(stderr, "\t-Ck\t\tAllows one to use localized key (must start with 0x)\n");
   fprintf(stderr, "\t\t\tinstead of passphrase.\n");
}

void snmpusm_optProc(int argc, char *const *argv, int opt) {
    switch (opt) {
    case 'C':
        while (*optarg) {
            switch (*optarg++) {
            case 'a':
                doauthkey = 1;
                break;

            case 'x':
                doprivkey = 1;
                break;

	    case 'k':
	        uselocalizedkey = 1;
		break;

	    case 'p':
                if (optind < argc) {
		    usmUserPublic_val =  argv[optind];
                } else {
                     throw ParseErrorBase("Bad -Cp option: no argument given\n");
                }
                optind++;
                break;

            case 'w':
                docreateandwait = 1;
                break;

	    case 'E': {
	        size_t ebuf_len = MAX_ENGINEID_LENGTH;
                u_char *ebuf;
                if (optind < argc) {
                    if (argv[optind]) {
                        ebuf = static_cast<u_char *>(malloc(ebuf_len));
                        if (ebuf == NULL) {
                           throw GenericErrorBase("malloc failure processing -CE option.\n");
                        }
                        if (!snmp_hex_to_binary(&ebuf, &ebuf_len, &usmUserEngineIDLen, 1,
                                                argv[optind])) {
		            free(ebuf);
                           throw ParseErrorBase("Bad usmUserEngineID value after -CE option.\n");
		        }
                        if (usmUserEngineID_allocated && usmUserEngineID != nullptr) {
                           free(usmUserEngineID);
                        }
		        usmUserEngineID = ebuf;
                        usmUserEngineID_allocated = true;
		        DEBUGMSGTL(("snmpusm", "usmUserEngineID set to: "));
		        DEBUGMSGHEX(("snmpusm", usmUserEngineID, usmUserEngineIDLen));
		        DEBUGMSG(("snmpusm", "\n"));
                    }
                } else {
                     throw ParseErrorBase("Bad -CE option: no argument given\n");
                }
                optind++;
                break;
            }

            default:
                  throw ParseErrorBase("Unknown flag passed to -C: " + std::string(1, optarg[-1]) +
                                       "\n");
            }
        }
        break;
    }
}

std::vector<std::string> snmpusm(std::vector<std::string> const &args,
                                 std::string const &init_app_name) {
   // Reference-counted initialization: only first thread calls init_snmp
   netsnmp_thread_init(init_app_name);

   SnmpusmStateGuard state_guard;

   int argc;
   std::unique_ptr<char *[], Deleter> argv = create_argv(args, argc);
   std::vector<std::string> return_vector;

   oid authKeyOid[MAX_OID_LEN] = {1, 3, 6, 1, 6, 3, 15, 1, 2, 2, 1, 6};
   oid ownAuthKeyOid[MAX_OID_LEN] = {1, 3, 6, 1, 6, 3, 15, 1, 2, 2, 1, 7};
   oid privKeyOid[MAX_OID_LEN] = {1, 3, 6, 1, 6, 3, 15, 1, 2, 2, 1, 9};
   oid ownPrivKeyOid[MAX_OID_LEN] = {1, 3, 6, 1, 6, 3, 15, 1, 2, 2, 1, 10};
   oid usmUserCloneFrom[MAX_OID_LEN] = {1, 3, 6, 1, 6, 3, 15, 1, 2, 2, 1, 4};
   oid usmUserSecurityName[MAX_OID_LEN] = {1, 3, 6, 1, 6, 3, 15, 1, 2, 2, 1, 3};
   oid usmUserPublic[MAX_OID_LEN] = {1, 3, 6, 1, 6, 3, 15, 1, 2, 2, 1, 11};
   oid usmUserStatus[MAX_OID_LEN] = {1, 3, 6, 1, 6, 3, 15, 1, 2, 2, 1, 13};
   oid *authKeyChange = authKeyOid;
   oid *privKeyChange = privKeyOid;

#if defined(HAVE_OPENSSL_DH_H) && defined(HAVE_LIBCRYPTO)
   oid usmDHUserAuthKeyChange[MAX_OID_LEN] = {1, 3, 6, 1, 3, 101, 1, 1, 2, 1, 1};
   oid usmDHUserPrivKeyChange[MAX_OID_LEN] = {1, 3, 6, 1, 3, 101, 1, 1, 2, 1, 3};
   oid usmDHUserOwnAuthKeyChange[MAX_OID_LEN] = {1, 3, 6, 1, 3, 101, 1, 1, 2, 1, 2};
   oid usmDHUserOwnPrivKeyChange[MAX_OID_LEN] = {1, 3, 6, 1, 3, 101, 1, 1, 2, 1, 4};
   oid *dhauthKeyChange = usmDHUserAuthKeyChange;
   oid *dhprivKeyChange = usmDHUserPrivKeyChange;
#endif /* HAVE_OPENSSL_DH_H && HAVE_LIBCRYPTO */

   netsnmp_session session;
   std::unique_ptr<void, SnmpSingleSessionCloser> ss;
   netsnmp_pdu *response = nullptr;

    int             arg;
    size_t          name_length = USM_OID_LEN;
    size_t          name_length2 = USM_OID_LEN;
    int             status;
    int             rval;
    int             command = 0;
    long            longvar;

   size_t oldKu_len = SNMP_MAXBUF_SMALL;
   size_t newKu_len = SNMP_MAXBUF_SMALL;
   size_t oldkul_len = SNMP_MAXBUF_SMALL;
   size_t oldkulpriv_len = SNMP_MAXBUF_SMALL;
   size_t newkulpriv_len = SNMP_MAXBUF_SMALL;
   size_t newkul_len = SNMP_MAXBUF_SMALL;
   size_t keychange_len = SNMP_MAXBUF_SMALL;
   size_t keychangepriv_len = SNMP_MAXBUF_SMALL;

   char const *newpass = nullptr;
   char const *oldpass = nullptr;
   u_char oldKu[SNMP_MAXBUF_SMALL];
   u_char newKu[SNMP_MAXBUF_SMALL];
   u_char oldkul[SNMP_MAXBUF_SMALL];
   u_char oldkulpriv[SNMP_MAXBUF_SMALL];
   u_char newkulpriv[SNMP_MAXBUF_SMALL];
   u_char newkul[SNMP_MAXBUF_SMALL];
   u_char keychange[SNMP_MAXBUF_SMALL];
   u_char keychangepriv[SNMP_MAXBUF_SMALL];

    SOCK_STARTUP;
   SockCleanupGuard sock_cleanup_guard;
   NetsnmpSessionCleanupGuard session_cleanup_guard;

   putenv(strdup("POSIXLY_CORRECT=1"));

   // Serialize Net-SNMP global setup: snmp_parse_args modifies shared Net-SNMP
   // global state (option parsing, DS library settings).
   {
      std::lock_guard<std::mutex> setup_lock(g_netsnmp_setup_mutex);

      netsnmp_register_loghandler(NETSNMP_LOGHANDLER_NONE, 0);
      netsnmp_ds_set_int(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_MIB_WARNINGS, 0);
      switch (arg = snmp_parse_args(argc, argv.get(), &session, "C:", snmpusm_optProc)) {
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
   }

    if (arg >= argc) {
      throw ParseErrorBase("Please specify an operation to perform.\n");
    }

    /*
     * open an SNMP session 
     * Note:  this needs to obtain the engineID used below 
     */
    session.flags &= ~SNMP_FLAGS_DONT_PROBE;
   ss.reset(snmp_sess_open(&session));
   if (!ss) {
      snmp_sess_perror_exception("snmpusm", &session);
    }

   netsnmp_session *sess = snmp_sess_session(ss.get());

    /*
    * set usmUserEngineID from sess->contextEngineID
     *   if not already set (via -CE)
     */
   if (usmUserEngineID == nullptr) {
      usmUserEngineID = sess->contextEngineID;
      usmUserEngineIDLen = sess->contextEngineIDLen;
    }

    /*
     * create PDU for SET request and add object names and values to request 
     */
   std::unique_ptr<netsnmp_pdu, SnmpPduDeleter> pdu(snmp_pdu_create(SNMP_MSG_SET));
    if (!pdu) {
      throw GenericErrorBase("Failed to create request\n");
    }

    if (strcmp(argv[arg], CMD_PASSWD_NAME) == 0) {
      char const *passwd_user = nullptr;

        command = CMD_PASSWD;
      if (++arg < argc) {
            oldpass = argv[arg];
      }
      if (++arg < argc) {
            newpass = argv[arg];
      }
      if (++arg < argc) {
            passwd_user = argv[arg];
      }

      if (doprivkey == 0 && doauthkey == 0) {
            doprivkey = doauthkey = 1;
      }

      if (newpass == nullptr || strlen(newpass) < USM_LENGTH_P_MIN) {
         throw ParseErrorBase("New passphrase must be greater than " +
                              std::to_string(USM_LENGTH_P_MIN) + " characters in length.\n");
        }

      if (oldpass == nullptr || strlen(oldpass) < USM_LENGTH_P_MIN) {
         throw ParseErrorBase("Old passphrase must be greater than " +
                              std::to_string(USM_LENGTH_P_MIN) + " characters in length.\n");
        }

      DEBUGMSGTL(("9:usm:passwd",
                  "oldpass len %" NETSNMP_PRIz "d, newpass len %" NETSNMP_PRIz "d\n",
                    strlen(oldpass), strlen(newpass)));

        /* 
         * Change the user supplied on command line.
         */
      if ((passwd_user != nullptr) && (strlen(passwd_user) > 0)) {
            SNMP_FREE(session.securityName);
            session.securityName = strdup(passwd_user);
        } else {
            /*
             * Use own key object if no user was supplied.
             */
            authKeyChange = ownAuthKeyOid;
            privKeyChange = ownPrivKeyOid;
        }

        /*
         * do we have a securityName?  If not, copy the default 
         */
      if (session.securityName == nullptr) {
         char const *default_secname =
             netsnmp_ds_get_string(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_SECNAME);
         if (default_secname != nullptr) {
            session.securityName = strdup(default_secname);
         } else {
            throw ParseErrorBase("No securityName specified.\n");
        }
      }

        /*
         * the old Ku is in the session, but we need the new one 
         */
      if (session.securityAuthProto == nullptr) {
         size_t auth_len = 0;
         oid const *def = get_default_authtype(&auth_len);
         session.securityAuthProtoLen = auth_len;
         session.securityAuthProto = snmp_duplicate_objid(def, session.securityAuthProtoLen);
        }
      if (session.securityAuthProto == nullptr) {
#ifndef NETSNMP_DISABLE_MD5
         session.securityAuthProtoLen = OID_LENGTH(usmHMACMD5AuthProtocol);
            session.securityAuthProto =
             snmp_duplicate_objid(usmHMACMD5AuthProtocol, session.securityAuthProtoLen);
#else
         session.securityAuthProtoLen = OID_LENGTH(usmHMACSHA1AuthProtocol);
            session.securityAuthProto =
             snmp_duplicate_objid(usmHMACSHA1AuthProtocol, session.securityAuthProtoLen);
#endif
        }

	if (uselocalizedkey && (strncmp(oldpass, "0x", 2) == 0)) {
	    u_char *buf;
	    size_t buf_len = SNMP_MAXBUF_SMALL;
         buf = static_cast<u_char *>(malloc(buf_len * sizeof(u_char)));
         if (!buf) {
            throw GenericErrorBase("malloc failure generating old Kul\n");
         }

         oldkul_len = 0;
         if (!snmp_hex_to_binary(&buf, &buf_len, &oldkul_len, 0, oldpass)) {
            SNMP_FREE(buf);
            throw GenericErrorBase("generating the old Kul from localized key failed\n");
	    }
	    
	    memcpy(oldkul, buf, oldkul_len);
	    SNMP_FREE(buf);
      } else {
         rval = generate_Ku(session.securityAuthProto, session.securityAuthProtoLen,
                            reinterpret_cast<u_char const *>(oldpass), strlen(oldpass), oldKu,
                            &oldKu_len);
	    
	    if (rval != SNMPERR_SUCCESS) {
            throw GenericErrorBase("generating the old Ku failed\n");
	    }

         rval =
             generate_kul(session.securityAuthProto, session.securityAuthProtoLen, usmUserEngineID,
                          usmUserEngineIDLen, oldKu, oldKu_len, oldkul, &oldkul_len);
	    
	    if (rval != SNMPERR_SUCCESS) {
            throw GenericErrorBase("generating the old Kul failed\n");
	    }
            DEBUGMSGTL(("9:usm:passwd", "oldkul len %" NETSNMP_PRIz "d\n", oldkul_len));
	}

	if (uselocalizedkey && (strncmp(newpass, "0x", 2) == 0)) {
	    u_char *buf;
	    size_t buf_len = SNMP_MAXBUF_SMALL;
         buf = static_cast<u_char *>(malloc(buf_len * sizeof(u_char)));
         if (!buf) {
            throw GenericErrorBase("malloc failure generating new Kul\n");
         }

         newkul_len = 0;
         if (!snmp_hex_to_binary(&buf, &buf_len, &newkul_len, 0, newpass)) {
            SNMP_FREE(buf);
            throw GenericErrorBase("generating the new Kul from localized key failed\n");
	    }
	    
	    memcpy(newkul, buf, newkul_len);
	    SNMP_FREE(buf);
	} else {
         rval = generate_Ku(session.securityAuthProto, session.securityAuthProtoLen,
                            reinterpret_cast<u_char const *>(newpass), strlen(newpass), newKu,
                            &newKu_len);

            if (rval != SNMPERR_SUCCESS) {
            throw GenericErrorBase("generating the new Ku failed\n");
            }

         rval =
             generate_kul(session.securityAuthProto, session.securityAuthProtoLen, usmUserEngineID,
                          usmUserEngineIDLen, newKu, newKu_len, newkul, &newkul_len);

	    if (rval != SNMPERR_SUCCESS) {
            throw GenericErrorBase("generating the new Kul failed\n");
	    }
            DEBUGMSGTL(("9:usm:passwd", "newkul len %" NETSNMP_PRIz "d\n", newkul_len));
	}

        if (doprivkey) {
         int privtype;
         size_t properlength;
         u_char *okp = oldkulpriv;
         u_char *nkp = newkulpriv;
            if (!session.securityPrivProto) {
            throw ParseErrorBase(
                "no encryption type specified, which I need in order to know to change the key\n");
            }

         privtype = sc_get_privtype(session.securityPrivProto, session.securityPrivProtoLen);
            properlength = sc_get_proper_priv_length_bytype(privtype);
         if (USM_CREATE_USER_PRIV_DES == privtype) {
            properlength *= 2;
         }
         DEBUGMSGTL(("9:usm:passwd", "proper len %zu\n", properlength));
            oldkulpriv_len = oldkul_len;
            newkulpriv_len = newkul_len;
            memcpy(oldkulpriv, oldkul, oldkulpriv_len);
            memcpy(newkulpriv, newkul, newkulpriv_len);

            if (oldkulpriv_len > properlength) {
                oldkulpriv_len = newkulpriv_len = properlength;
         } else if (oldkulpriv_len < properlength) {
            rval = netsnmp_extend_kul(
                properlength, session.securityAuthProto, session.securityAuthProtoLen, privtype,
                usmUserEngineID, usmUserEngineIDLen, &okp, &oldkulpriv_len, sizeof(oldkulpriv));
            if (rval != SNMPERR_SUCCESS) {
               throw GenericErrorBase("extending the old priv Kul failed\n");
            }
            rval = netsnmp_extend_kul(
                properlength, session.securityAuthProto, session.securityAuthProtoLen, privtype,
                usmUserEngineID, usmUserEngineIDLen, &nkp, &newkulpriv_len, sizeof(newkulpriv));
            if (rval != SNMPERR_SUCCESS) {
               throw GenericErrorBase("extending the new priv Kul failed\n");
            }
        }
      }

	if (doauthkey) {
         rval = encode_keychange(session.securityAuthProto, session.securityAuthProtoLen, oldkul,
                                 oldkul_len, newkul, newkul_len, keychange, &keychange_len);

	  if (rval != SNMPERR_SUCCESS) {
            throw GenericErrorBase("encoding the keychange failed\n");
	  }
	}

	if (doprivkey) {
         DEBUGMSGTL(("9:usm:passwd:encode",
                     "proper len %" NETSNMP_PRIz "d, old_len %" NETSNMP_PRIz
                     "d, new_len %" NETSNMP_PRIz "d\n",
                        oldkulpriv_len, oldkulpriv_len, newkulpriv_len));
         rval = encode_keychange(session.securityAuthProto, session.securityAuthProtoLen,
                                 oldkulpriv, oldkulpriv_len, newkulpriv, newkulpriv_len,
                                keychangepriv, &keychangepriv_len);

         DEBUGMSGTL(
             ("9:usm:passwd:encode", "keychange len %" NETSNMP_PRIz "d\n", keychangepriv_len));
	  if (rval != SNMPERR_SUCCESS) {
            throw GenericErrorBase("encoding the keychange failed\n");
	  }
	}

        if (doauthkey) {
         setup_oid(authKeyChange, &name_length, usmUserEngineID, usmUserEngineIDLen,
                      session.securityName);
         snmp_pdu_add_variable(pdu.get(), authKeyChange, name_length, ASN_OCTET_STR, keychange,
                               keychange_len);
        }
        if (doprivkey) {
         setup_oid(privKeyChange, &name_length2, usmUserEngineID, usmUserEngineIDLen,
                      session.securityName);
         snmp_pdu_add_variable(pdu.get(), privKeyChange, name_length2, ASN_OCTET_STR, keychangepriv,
                               keychangepriv_len);
        }

    } else if (strcmp(argv[arg], CMD_CREATE_NAME) == 0) {
        if (++arg >= argc) {
         throw ParseErrorBase("You must specify the user name to create\n");
        }

        command = CMD_CREATE;

        if (++arg < argc) {
         setup_oid(usmUserStatus, &name_length, usmUserEngineID, usmUserEngineIDLen, argv[arg - 1]);
            if (docreateandwait) {
                longvar = RS_CREATEANDWAIT;
            } else {
                longvar = RS_CREATEANDGO;
            }
         snmp_pdu_add_variable(pdu.get(), usmUserStatus, name_length, ASN_INTEGER,
                               reinterpret_cast<u_char *>(&longvar), sizeof(longvar));

            name_length = USM_OID_LEN;
         setup_oid(usmUserCloneFrom, &name_length, usmUserEngineID, usmUserEngineIDLen,
                      argv[arg - 1]);
         setup_oid(usmUserSecurityName, &name_length2, usmUserEngineID, usmUserEngineIDLen,
                      argv[arg]);
         snmp_pdu_add_variable(pdu.get(), usmUserCloneFrom, name_length, ASN_OBJECT_ID,
                               reinterpret_cast<u_char *>(usmUserSecurityName),
                                  sizeof(oid) * name_length2);
        } else {
         setup_oid(usmUserStatus, &name_length, usmUserEngineID, usmUserEngineIDLen, argv[arg - 1]);
            longvar = RS_CREATEANDWAIT;
         snmp_pdu_add_variable(pdu.get(), usmUserStatus, name_length, ASN_INTEGER,
                               reinterpret_cast<u_char *>(&longvar), sizeof(longvar));
        }

    } else if (strcmp(argv[arg], CMD_CLONEFROM_NAME) == 0) {
        if (++arg >= argc) {
         throw ParseErrorBase("You must specify the user name to operate on\n");
        }

        command = CMD_CLONEFROM;
      setup_oid(usmUserStatus, &name_length, usmUserEngineID, usmUserEngineIDLen, argv[arg]);
        longvar = RS_ACTIVE;
      snmp_pdu_add_variable(pdu.get(), usmUserStatus, name_length, ASN_INTEGER,
                            reinterpret_cast<u_char *>(&longvar), sizeof(longvar));
        name_length = USM_OID_LEN;
      setup_oid(usmUserCloneFrom, &name_length, usmUserEngineID, usmUserEngineIDLen, argv[arg]);

        if (++arg >= argc) {
         throw ParseErrorBase("You must specify the user name to clone from\n");
        }

      setup_oid(usmUserSecurityName, &name_length2, usmUserEngineID, usmUserEngineIDLen, argv[arg]);
      snmp_pdu_add_variable(pdu.get(), usmUserCloneFrom, name_length, ASN_OBJECT_ID,
                            reinterpret_cast<u_char *>(usmUserSecurityName),
                              sizeof(oid) * name_length2);

    } else if (strcmp(argv[arg], CMD_DELETE_NAME) == 0) {
        if (++arg >= argc) {
         throw ParseErrorBase("You must specify the user name to delete\n");
        }

        command = CMD_DELETE;
      setup_oid(usmUserStatus, &name_length, usmUserEngineID, usmUserEngineIDLen, argv[arg]);
        longvar = RS_DESTROY;
      snmp_pdu_add_variable(pdu.get(), usmUserStatus, name_length, ASN_INTEGER,
                            reinterpret_cast<u_char *>(&longvar), sizeof(longvar));

    } else if (strcmp(argv[arg], CMD_ACTIVATE_NAME) == 0) {
        if (++arg >= argc) {
         throw ParseErrorBase("You must specify the user name to activate\n");
        }

        command = CMD_ACTIVATE;
      setup_oid(usmUserStatus, &name_length, usmUserEngineID, usmUserEngineIDLen, argv[arg]);
        longvar = RS_ACTIVE;
      snmp_pdu_add_variable(pdu.get(), usmUserStatus, name_length, ASN_INTEGER,
                            reinterpret_cast<u_char *>(&longvar), sizeof(longvar));

   } else if (strcmp(argv[arg], CMD_DEACTIVATE_NAME) == 0) {
        if (++arg >= argc) {
         throw ParseErrorBase("You must specify the user name to deactivate\n");
        }

        command = CMD_DEACTIVATE;
      setup_oid(usmUserStatus, &name_length, usmUserEngineID, usmUserEngineIDLen, argv[arg]);
        longvar = RS_NOTINSERVICE;
      snmp_pdu_add_variable(pdu.get(), usmUserStatus, name_length, ASN_INTEGER,
                            reinterpret_cast<u_char *>(&longvar), sizeof(longvar));

#if defined(HAVE_OPENSSL_DH_H) && defined(HAVE_LIBCRYPTO)
    } else if (strcmp(argv[arg], CMD_CHANGEKEY_NAME) == 0) {
      char const *passwd_user;
      netsnmp_pdu *dhpdu = nullptr;
      netsnmp_pdu *dhresponse_raw = nullptr;
      netsnmp_variable_list *vars = nullptr;
      netsnmp_variable_list *dhvar = nullptr;

        command = CMD_CHANGEKEY;
        name_length = DH_USM_OID_LEN;
        name_length2 = DH_USM_OID_LEN;

      passwd_user = (++arg < argc) ? argv[arg] : nullptr;

      if (doprivkey == 0 && doauthkey == 0) {
            doprivkey = doauthkey = 1;
      }

      if ((passwd_user != nullptr) && (strlen(passwd_user) > 0)) {
         SNMP_FREE(session.securityName);
            session.securityName = strdup(passwd_user);
        } else {
            dhauthKeyChange = usmDHUserOwnAuthKeyChange;
            dhprivKeyChange = usmDHUserOwnPrivKeyChange;
        }

      if (session.securityName == nullptr) {
         char const *default_secname =
             netsnmp_ds_get_string(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_SECNAME);
         if (default_secname != nullptr) {
            session.securityName = strdup(default_secname);
         } else {
            throw ParseErrorBase("No securityName specified.\n");
        }
      }

        dhpdu = snmp_pdu_create(SNMP_MSG_GET);
        if (!dhpdu) {
         throw GenericErrorBase("Failed to create DH request\n");
        }

        snmp_add_null_var(dhpdu, usmDHParameters, usmDHParameters_len);
        
        if (doauthkey) {
         setup_oid(dhauthKeyChange, &name_length, usmUserEngineID, usmUserEngineIDLen,
                      session.securityName);
            snmp_add_null_var(dhpdu, dhauthKeyChange, name_length);
        }
            
        if (doprivkey) {
         setup_oid(dhprivKeyChange, &name_length2, usmUserEngineID, usmUserEngineIDLen,
                      session.securityName);
            snmp_add_null_var(dhpdu, dhprivKeyChange, name_length2);
        }

      status = snmp_sess_synch_response(static_cast<struct session_list *>(ss.get()), dhpdu,
                                        &dhresponse_raw);
      std::unique_ptr<netsnmp_pdu, SnmpPduDeleter> dhresponse(dhresponse_raw);

      if (status != SNMPERR_SUCCESS || !dhresponse || dhresponse->errstat != SNMP_ERR_NOERROR ||
          !dhresponse->variables || dhresponse->variables->type != ASN_OCTET_STR) {
         if (dhresponse && dhresponse->variables && dhresponse->variables->type != ASN_OCTET_STR) {
            throw GenericErrorBase(
                "Can't get diffie-helman exchange from the agent\n"
                        "  (maybe it doesn't support the SNMP-USM-DH-OBJECTS-MIB MIB)\n");
            }
         if (status == STAT_TIMEOUT) {
            throw TimeoutErrorBase("Timeout: No Response from " +
                                   std::string(session.peername ? session.peername : "") + "\n");
        }
         snmp_single_sess_perror_exception("snmpusm", ss.get());
      }
        
        dhvar = dhresponse->variables;
        vars = dhvar->next_variable;
        if (doauthkey) {
         if (get_USM_DH_key(
                 vars, dhvar,
                 sc_get_properlength(sess->securityAuthProto, sess->securityAuthProtoLen),
                 pdu.get(), "auth", dhauthKeyChange, name_length,
                 return_vector) != SNMPERR_SUCCESS) {
            throw GenericErrorBase("Failed to compute Diffie-Hellman auth key\n");
            }
         if (vars) {
            vars = vars->next_variable;
        }
      }
        if (doprivkey) {
            size_t dhprivKeyLen = 0;
         int privtype = sc_get_privtype(sess->securityPrivProto, sess->securityPrivProtoLen);
            dhprivKeyLen = sc_get_proper_priv_length_bytype(privtype);
         if (USM_CREATE_USER_PRIV_DES == privtype) {
            dhprivKeyLen *= 2;
            }
         if (get_USM_DH_key(vars, dhvar, dhprivKeyLen, pdu.get(), "priv", dhprivKeyChange,
                            name_length2, return_vector) != SNMPERR_SUCCESS) {
            throw GenericErrorBase("Failed to compute Diffie-Hellman priv key\n");
         }
         if (vars) {
            vars = vars->next_variable;
        }
      }
#endif /* HAVE_OPENSSL_DH_H && HAVE_LIBCRYPTO */
    } else {
      throw ParseErrorBase("Unknown command: " + std::string(argv[arg]) + "\n");
    }

    /*
     * add usmUserPublic if specified (via -Cp)
     */
    if (usmUserPublic_val) {
      if (session.securityName == nullptr) {
         char const *default_secname =
             netsnmp_ds_get_string(NETSNMP_DS_LIBRARY_ID, NETSNMP_DS_LIB_SECNAME);
         if (default_secname != nullptr) {
            session.securityName = strdup(default_secname);
         } else {
            throw ParseErrorBase("No securityName specified for -Cp option.\n");
         }
      }
        name_length = USM_OID_LEN;
      setup_oid(usmUserPublic, &name_length, usmUserEngineID, usmUserEngineIDLen,
		  session.securityName);
      snmp_pdu_add_variable(pdu.get(), usmUserPublic, name_length, ASN_OCTET_STR,
                            reinterpret_cast<u_char const *>(usmUserPublic_val),
			      strlen(usmUserPublic_val));	  
    }

    /*
     * do the request 
     */
   status = snmp_sess_synch_response(static_cast<struct session_list *>(ss.get()), pdu.release(),
                                     &response);
   std::unique_ptr<netsnmp_pdu, SnmpPduDeleter> response_guard(response);

    if (status == STAT_SUCCESS) {
      snmp_check_null_response(response);
            if (response->errstat == SNMP_ERR_NOERROR) {
         return_vector.push_back(successNotes[command - 1]);
            } else {
         std::string err_msg =
             "Error in packet.\nReason: " + std::string(snmp_errstring(response->errstat)) + "\n";

                if (response->errindex != 0) {
                    int             count;
                    netsnmp_variable_list *vars;
            err_msg += "Failed object: ";
            for (count = 1, vars = response->variables; vars && count != response->errindex;
                         vars = vars->next_variable, count++)
                        /*EMPTY*/;
            if (vars) {
               err_msg += print_objid_to_string(vars->name, vars->name_length);
                }
            err_msg += "\n";
            }
         throw PacketErrorBase(err_msg);
        }
    } else if (status == STAT_TIMEOUT) {
      throw TimeoutErrorBase("Timeout: No Response from " +
                             std::string(session.peername ? session.peername : "") + "\n");
    } else {                    /* status == STAT_ERROR */
      snmp_single_sess_perror_exception("snmpusm", ss.get());
    }

   return return_vector;
}
