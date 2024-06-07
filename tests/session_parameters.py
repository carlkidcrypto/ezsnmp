SESS_V1_ARGS = {
    "version": 1,
    "hostname": "localhost",
    "remote_port": 11161,
    "community": "public",
}

SESS_V2_ARGS = {
    "version": 2,
    "hostname": "localhost",
    "remote_port": 11161,
    "community": "public",
}

SESS_V3_MD5_DES_ARGS = {
    "version": 3,
    "hostname": "localhost",
    "remote_port": 11161,
    "auth_protocol": "MD5",
    "security_level": "authPriv",
    "security_username": "initial_md5_des",
    "privacy_protocol": "DES",
    "privacy_password": "priv_pass",
    "auth_password": "auth_pass",
}

SESS_V3_MD5_AES_ARGS = {
    "version": 3,
    "hostname": "localhost",
    "remote_port": 11161,
    "auth_protocol": "MD5",
    "security_level": "authPriv",
    "security_username": "initial_md5_aes",
    "privacy_protocol": "AES",
    "privacy_password": "priv_pass",
    "auth_password": "auth_pass",
}

SESS_V3_SHA_AES_ARGS = {
    "version": 3,
    "hostname": "localhost",
    "remote_port": 11161,
    "auth_protocol": "SHA",
    "security_level": "authPriv",
    "security_username": "secondary_sha_aes",
    "privacy_protocol": "AES",
    "privacy_password": "priv_second",
    "auth_password": "auth_second",
}

SESS_V3_SHA_NO_PRIV_ARGS = {
    "version": 3,
    "hostname": "localhost",
    "remote_port": 11161,
    "auth_protocol": "SHA",
    "security_level": "authNoPriv",
    "security_username": "secondary_sha_no_priv",
    "auth_password": "auth_second",
}

SESS_V3_MD5_NO_PRIV_ARGS = {
    "version": 3,
    "hostname": "localhost",
    "remote_port": 11161,
    "auth_protocol": "MD5",
    "security_level": "auth_without_privacy",
    "security_username": "initial_md5_no_priv",
    "auth_password": "auth_pass",
}
