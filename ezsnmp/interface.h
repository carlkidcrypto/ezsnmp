/* This is the header file to the 'interface.cpp' file. Will include things like
 * function definitions, enums, etc.
 */

/******************************************************************************
 *
 * Defines for the 'interface.c' file are listed below
 *
 ******************************************************************************/

#define APPNAME "python"
/*
 * In snmpv1 when using retry_nosuch we need to track the
 * index of each bad OID in the responses using a bitarray;
 * DEFAULT_NUM_BAD_OIDS is a tradeoff to avoid allocating
 * heavily on the heap; if we need to track more, we can
 * just malloc on the heap.
 */
#define DEFAULT_NUM_BAD_OIDS (sizeof(bitarray) * 8 * 3)
#define STRLEN(x) ((x) ? strlen((x)) : 0)
#define SUCCESS (1)
#define FAILURE (0)
#define VARBIND_TAG_F (0)
#define VARBIND_IID_F (1)
#define VARBIND_VAL_F (2)
#define VARBIND_TYPE_F (3)
#define TYPE_UNKNOWN (0)
#define MAX_TYPE_NAME_LEN (32)
#define STR_BUF_SIZE ((MAX_TYPE_NAME_LEN) * (MAX_OID_LEN))
#define MAX_VALUE_SIZE (65536)
#define MAX_INVALID_OIDS (MAX_VALUE_SIZE / MIN_OID_LEN)
#define ENG_ID_BUF_SIZE (32)
#define NO_RETRY_NOSUCH (0)
#define USE_NUMERIC_OIDS (0x08)
#define NON_LEAF_NAME (0x04)
#define USE_LONG_NAMES (0x02)
#define FAIL_ON_NULL_IID (0x01)
#define NO_FLAGS (0x00)
#define SAFE_FREE(x)   \
    do                 \
    {                  \
        if (x != NULL) \
        {              \
            free(x);   \
        }              \
    } while (0)

// Available from 5.6.x and older
#ifdef HAVE_EVP_MD_CTX_CREATE
struct session_list
{
    struct session_list *next;
    netsnmp_session *session;
    netsnmp_transport *transport;
    struct snmp_internal_session *internal;
};
#endif

/******************************************************************************
 *
 * Data structures used in the 'interface.c' file are listed below
 *
 ******************************************************************************/

typedef netsnmp_session SnmpSession;
/*
 * This structure is attached to the ezsnmp.Session
 * object as a Python Capsule (or CObject).
 *
 * This allows a one time allocation of large buffers
 * without resorting to (unnecessary) allocation on the
 * stack, but also remains thread safe; as long as only
 * one Session object is restricted to each thread.
 *
 * This is allocated in create_session_capsule()
 * and later (automatically via garbage collection) destroyed
 * delete_session_capsule().
 */
struct session_capsule_ctx
{
    /*
     * Technically this should be a (void *), but this probably
     * won't ever change in Net-SNMP.
     */
    netsnmp_session *handle;
    /* buf is reusable and stores OID values and names */
    u_char buf[MAX_VALUE_SIZE];
    /* err_str is used to fetch the error message from net-snmp libs */
    char err_str[STR_BUF_SIZE];
    /* used by netsnmp_{get,getnext,set}. */
    oid oid_arr[MAX_OID_LEN];
    /*
     * invalid_oids is a bitarray for maintaining invalid OIDS when performing
     * SNMPv1 requests.
     *
     * Note: prior to use, the number of bits required should be cleared.
     */
    unsigned char invalid_oids_buf[MAX_INVALID_OIDS / CHAR_BIT];
    bitarray *invalid_oids;
};

enum
{
    INFO,
    WARNING,
    ERROR,
    DEBUG,
    EXCEPTION
};

/******************************************************************************
 *
 * Function definitions for the 'interface.cpp' file are listed below
 *
 ******************************************************************************/

void PyObject_deleter(PyObject *obj);
void *compat_netsnmp_memdup(const void *from, size_t size);
int __match_algo(int is_auth, char *algo, oid **output, size_t *len);
void __libraries_init();
void __libraries_free();
int __is_leaf(struct tree *tp);
int __translate_appl_type(char *typestr);
int __translate_asn_type(int type);
int __snprint_value(char *buf, size_t buf_len,
                    netsnmp_variable_list *var,
                    struct tree *tp, int type, int flag);
int __sprint_num_objid(char *buf, oid *objid, int len);
int __scan_num_objid(char *buf, oid *objid, size_t *len);
int __get_type_str(int type, char *str, int log_error);
int __get_label_iid(char *name, char **last_label, char **iid,
                    int flag);
struct tree *__tag2oid(char *tag, char *iid, oid *oid_arr,
                       size_t *oid_arr_len, int *type, int best_guess);
int __concat_oid_str(oid *doid_arr, size_t *doid_arr_len, char *soid_str);
int __add_var_val_str(netsnmp_pdu *pdu, oid *name, int name_length,
                      char *val, int len, int type);
int __send_sync_pdu(netsnmp_session *ss, netsnmp_pdu **pdu,
                    netsnmp_pdu **response, int retry_nosuch,
                    char *err_str, int *err_num, int *err_ind,
                    bitarray *invalid_oids);
void __remove_user_from_cache(struct session_list *ss);
PyObject *py_netsnmp_construct_varbind(void);
int py_netsnmp_attr_string(PyObject *obj, char *attr_name, char **val,
                           Py_ssize_t *len, PyObject **attr_bytes);
long long py_netsnmp_attr_long(PyObject *obj, char *attr_name);
int py_netsnmp_attr_set_string(PyObject *obj, char *attr_name,
                               char *val, size_t len);
void __py_netsnmp_update_session_errors(PyObject *session,
                                        char *err_str, int err_num,
                                        int err_ind);
PyObject *create_session_capsule(SnmpSession *session);
void *get_session_handle_from_capsule(PyObject *session_capsule);
#ifdef USE_DEPRECATED_COBJECT_API
void delete_session_capsule(void *session_ptr);
#else
void delete_session_capsule(PyObject *session_capsule);
#endif
PyObject *netsnmp_create_session(PyObject *self, PyObject *args);
PyObject *netsnmp_create_session_v3(PyObject *self, PyObject *args);
PyObject *netsnmp_create_session_tunneled(PyObject *self,
                                          PyObject *args);
PyObject *netsnmp_get(PyObject *self, PyObject *args);
PyObject *netsnmp_getnext(PyObject *self, PyObject *args);
PyObject *netsnmp_walk(PyObject *self, PyObject *args);
PyObject *netsnmp_getbulk(PyObject *self, PyObject *args);
PyObject *netsnmp_bulkwalk(PyObject *self, PyObject *args);
PyObject *netsnmp_set(PyObject *self, PyObject *args);
PyObject *py_get_logger(char *logger_name);
void py_log_msg(int log_level, char *printf_fmt, ...);