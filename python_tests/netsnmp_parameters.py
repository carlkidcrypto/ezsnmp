NETSNMP_SESS_V1_ARGS = [
    "-v",
    "1",
    "-c",
    "public",
    "localhost:11161",
]

NETSNMP_SESS_V2_ARGS = [
    "-v",
    "2c",
    "-c",
    "public",
    "localhost:11161",
]

NETSNMP_SESS_V3_MD5_DES_ARGS = [
    "-v",
    "3",
    "-a",
    "MD5",
    "-l",
    "authPriv",
    "-u",
    "initial_md5_des",
    "-x",
    "DES",
    "-X",
    "priv_pass",
    "-A",
    "auth_pass",
    "localhost:11161",
]

NETSNMP_SESS_V3_MD5_AES_ARGS = [
    "-v",
    "3",
    "-a",
    "MD5",
    "-l",
    "authPriv",
    "-u",
    "initial_md5_aes",
    "-x",
    "AES",
    "-X",
    "priv_pass",
    "-A",
    "auth_pass",
    "localhost:11161",
]

NETSNMP_SESS_V3_SHA_AES_ARGS = [
    "-v",
    "3",
    "-a",
    "SHA",
    "-l",
    "authPriv",
    "-u",
    "secondary_sha_aes",
    "-x",
    "AES",
    "-X",
    "priv_second",
    "-A",
    "auth_second",
    "localhost:11161",
]


NETSNMP_SESS_V3_SHA_NO_PRIV_ARGS = [
    "-v",
    "3",
    "-a",
    "SHA",
    "-l",
    "authNoPriv",
    "-u",
    "secondary_sha_no_priv",
    "-A",
    "auth_second",
    "localhost:11161",
]

NETSNMP_SESS_V3_MD5_NO_PRIV_ARGS = [
    "-v",
    "3",
    "-a",
    "MD5",
    "-l",
    "authNoPriv",
    "-u",
    "initial_md5_no_priv",
    "-A",
    "auth_pass",
    "localhost:11161",
]
