import sys

# Python 3.12+ requires longer timeouts for SNMPv3 crypto operations
# due to changes in SSL/TLS and cryptography library integration
SNMPV3_TIMEOUT = "15" if sys.version_info >= (3, 12) else "5"
STANDARD_TIMEOUT = "5"
RETRIES = "3"

SESS_V1_ARGS = {
    "version": "1",
    "hostname": "localhost",
    "port_number": "11161",
    "community": "public",
    "timeout": STANDARD_TIMEOUT,
    "retries": RETRIES,
}

SESS_V2_ARGS = {
    "version": "2c",
    "hostname": "localhost",
    "port_number": "11161",
    "community": "public",
    "timeout": STANDARD_TIMEOUT,
    "retries": RETRIES,
}

SESS_V3_MD5_DES_ARGS = {
    "version": "3",
    "hostname": "localhost",
    "port_number": "11161",
    "auth_protocol": "MD5",
    "security_level": "authPriv",
    "security_username": "initial_md5_des",
    "privacy_protocol": "DES",
    "privacy_passphrase": "priv_pass",
    "auth_passphrase": "auth_pass",
    "timeout": SNMPV3_TIMEOUT,
    "retries": RETRIES,
}

SESS_V3_MD5_AES_ARGS = {
    "version": "3",
    "hostname": "localhost",
    "port_number": "11161",
    "auth_protocol": "MD5",
    "security_level": "authPriv",
    "security_username": "initial_md5_aes",
    "privacy_protocol": "AES",
    "privacy_passphrase": "priv_pass",
    "auth_passphrase": "auth_pass",
    "timeout": SNMPV3_TIMEOUT,
    "retries": RETRIES,
}

SESS_V3_SHA_AES_ARGS = {
    "version": "3",
    "hostname": "localhost",
    "port_number": "11161",
    "auth_protocol": "SHA",
    "security_level": "authPriv",
    "security_username": "secondary_sha_aes",
    "privacy_protocol": "AES",
    "privacy_passphrase": "priv_second",
    "auth_passphrase": "auth_second",
    "timeout": SNMPV3_TIMEOUT,
    "retries": RETRIES,
}

SESS_V3_SHA_NO_PRIV_ARGS = {
    "version": "3",
    "hostname": "localhost",
    "port_number": "11161",
    "auth_protocol": "SHA",
    "security_level": "authNoPriv",
    "security_username": "secondary_sha_no_priv",
    "auth_passphrase": "auth_second",
    "timeout": SNMPV3_TIMEOUT,
    "retries": RETRIES,
}

SESS_V3_MD5_NO_PRIV_ARGS = {
    "version": "3",
    "hostname": "localhost",
    "port_number": "11161",
    "auth_protocol": "MD5",
    "security_level": "authNoPriv",
    "security_username": "initial_md5_no_priv",
    "auth_passphrase": "auth_pass",
    "timeout": SNMPV3_TIMEOUT,
    "retries": RETRIES,
}
