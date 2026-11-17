import platform
import pytest

from ezsnmp.session import Session
from ezsnmp.exceptions import ConnectionError, ParseError, TimeoutError, PacketError
import faulthandler

faulthandler.enable()


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_print_enums_numerically(version):

    if version == "3" or version == 3:
        session = Session(
            version=version,
            hostname="localhost",
            port_number="11161",
            auth_protocol="SHA",
            security_level="authPriv",
            security_username="secondary_sha_aes",
            privacy_protocol="AES",
            privacy_passphrase="priv_second",
            auth_passphrase="auth_second",
            print_enums_numerically=True,
            print_full_oids=False,
            print_oids_numerically=False,
        )

        # Verify only enum option was set
        args = session.args

        assert args == (
            "-A",
            "auth_second",
            "-a",
            "SHA",
            "-X",
            "priv_second",
            "-x",
            "AES",
            "-r",
            "3",
            "-l",
            "authPriv",
            "-u",
            "secondary_sha_aes",
            "-t",
            "1",
            "-v",
            "3",
            "-O",
            "e",
            "localhost:11161",
        )

    else:
        session = Session(
            hostname="localhost:11161",
            version=version,
            print_enums_numerically=True,
            print_full_oids=False,
            print_oids_numerically=False,
        )

        # Verify only enum option was set
        args = session.args

        assert args == (
            "-c",
            "public",
            "-r",
            "3",
            "-t",
            "1",
            "-v",
            "2c" if version == 2 else f"{version}",
            "-O",
            "e",
            "localhost:11161",
        )

    # Verify session can do snmpget
    res = session.get(["ifAdminStatus.1"])
    assert len(res) == 1
    assert res[0].oid == "IF-MIB::ifAdminStatus"
    assert res[0].value == "1"
    assert res[0].type == "INTEGER"
    assert res[0].index == "1"

    # With print_enums_numerically=False
    # IF-MIB::ifAdminStatus
    # up(1)
    # INTEGER
    # 1

    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_print_full_oids(version):

    if version == "3" or version == 3:
        session = Session(
            version=version,
            hostname="localhost",
            port_number="11161",
            auth_protocol="SHA",
            security_level="authPriv",
            security_username="secondary_sha_aes",
            privacy_protocol="AES",
            privacy_passphrase="priv_second",
            auth_passphrase="auth_second",
            print_enums_numerically=False,
            print_full_oids=True,
            print_oids_numerically=False,
        )

        # Verify only enum option was set
        args = session.args

        assert args == (
            "-A",
            "auth_second",
            "-a",
            "SHA",
            "-X",
            "priv_second",
            "-x",
            "AES",
            "-r",
            "3",
            "-l",
            "authPriv",
            "-u",
            "secondary_sha_aes",
            "-t",
            "1",
            "-v",
            "3",
            "-O",
            "f",
            "localhost:11161",
        )

    else:
        session = Session(
            hostname="localhost:11161",
            version=version,
            print_enums_numerically=False,
            print_full_oids=True,
            print_oids_numerically=False,
        )

        # Verify only enum option was set
        args = session.args

        assert args == (
            "-c",
            "public",
            "-r",
            "3",
            "-t",
            "1",
            "-v",
            "2c" if version == 2 else f"{version}",
            "-O",
            "f",
            "localhost:11161",
        )

    # Verify session can do snmpget
    res = session.get(["ifAdminStatus.1"])
    assert len(res) == 1
    assert (
        res[0].oid
        == ".iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifAdminStatus"
    )
    assert res[0].value == "up(1)"
    assert res[0].type == "INTEGER"
    assert res[0].index == "1"

    # With print_enums_numerically=False
    # IF-MIB::ifAdminStatus
    # up(1)
    # INTEGER
    # 1

    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_print_oids_numerically(version):

    if version == "3" or version == 3:
        session = Session(
            version=version,
            hostname="localhost",
            port_number="11161",
            auth_protocol="SHA",
            security_level="authPriv",
            security_username="secondary_sha_aes",
            privacy_protocol="AES",
            privacy_passphrase="priv_second",
            auth_passphrase="auth_second",
            print_enums_numerically=False,
            print_full_oids=False,
            print_oids_numerically=True,
        )

        # Verify only enum option was set
        args = session.args

        assert args == (
            "-A",
            "auth_second",
            "-a",
            "SHA",
            "-X",
            "priv_second",
            "-x",
            "AES",
            "-r",
            "3",
            "-l",
            "authPriv",
            "-u",
            "secondary_sha_aes",
            "-t",
            "1",
            "-v",
            "3",
            "-O",
            "n",
            "localhost:11161",
        )

    else:
        session = Session(
            hostname="localhost:11161",
            version=version,
            print_enums_numerically=False,
            print_full_oids=False,
            print_oids_numerically=True,
        )

        # Verify only enum option was set
        args = session.args

        assert args == (
            "-c",
            "public",
            "-r",
            "3",
            "-t",
            "1",
            "-v",
            "2c" if version == 2 else f"{version}",
            "-O",
            "n",
            "localhost:11161",
        )

    # Verify session can do snmpget
    res = session.get(["ifAdminStatus.1"])
    assert len(res) == 1
    assert res[0].oid == ".1.3.6.1.2.1.2.2.1.7"
    assert res[0].value == "up(1)"
    assert res[0].type == "INTEGER"
    assert res[0].index == "1"

    # With print_enums_numerically=False
    # IF-MIB::ifAdminStatus
    # up(1)
    # INTEGER
    # 1

    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_print_options_all_set(version):

    if version == "3" or version == 3:
        session = Session(
            version=version,
            hostname="localhost",
            port_number="11161",
            auth_protocol="SHA",
            security_level="authPriv",
            security_username="secondary_sha_aes",
            privacy_protocol="AES",
            privacy_passphrase="priv_second",
            auth_passphrase="auth_second",
            print_enums_numerically=True,
            print_full_oids=True,
            print_oids_numerically=True,
        )

        # Verify only enum option was set
        args = session.args

        assert args == (
            "-A",
            "auth_second",
            "-a",
            "SHA",
            "-X",
            "priv_second",
            "-x",
            "AES",
            "-r",
            "3",
            "-l",
            "authPriv",
            "-u",
            "secondary_sha_aes",
            "-t",
            "1",
            "-v",
            "3",
            "-O",
            "e",
            "-O",
            "f",
            "-O",
            "n",
            "localhost:11161",
        )

    else:
        session = Session(
            hostname="localhost:11161",
            version=version,
            print_enums_numerically=True,
            print_full_oids=True,
            print_oids_numerically=True,
        )

        # Verify only enum option was set
        args = session.args

        assert args == (
            "-c",
            "public",
            "-r",
            "3",
            "-t",
            "1",
            "-v",
            "2c" if version == 2 else f"{version}",
            "-O",
            "e",
            "-O",
            "f",
            "-O",
            "n",
            "localhost:11161",
        )

    # Verify session can do snmpget
    res = session.get(["ifAdminStatus.1"])
    assert len(res) == 1
    assert res[0].oid == ".1.3.6.1.2.1.2.2.1.7"
    assert res[0].value == "1"
    assert res[0].type == "INTEGER"
    assert res[0].index == "1"

    # With print_enums_numerically=False
    # IF-MIB::ifAdminStatus
    # up(1)
    # INTEGER
    # 1

    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_print_options_two_set_true_true_false(version):

    if version == "3" or version == 3:
        session = Session(
            version=version,
            hostname="localhost",
            port_number="11161",
            auth_protocol="SHA",
            security_level="authPriv",
            security_username="secondary_sha_aes",
            privacy_protocol="AES",
            privacy_passphrase="priv_second",
            auth_passphrase="auth_second",
            print_enums_numerically=True,
            print_full_oids=True,
            print_oids_numerically=False,
        )

        # Verify only enum option was set
        args = session.args
        assert args == (
            "-A",
            "auth_second",
            "-a",
            "SHA",
            "-X",
            "priv_second",
            "-x",
            "AES",
            "-r",
            "3",
            "-l",
            "authPriv",
            "-u",
            "secondary_sha_aes",
            "-t",
            "1",
            "-v",
            "3",
            "-O",
            "e",
            "-O",
            "f",
            "localhost:11161",
        )

    else:
        session = Session(
            hostname="localhost:11161",
            version=version,
            print_enums_numerically=True,
            print_full_oids=True,
            print_oids_numerically=False,
        )

        # Verify only enum option was set
        args = session.args
        assert args == (
            "-c",
            "public",
            "-r",
            "3",
            "-t",
            "1",
            "-v",
            "2c" if version == 2 else f"{version}",
            "-O",
            "e",
            "-O",
            "f",
            "localhost:11161",
        )

    # Verify session can do snmpget
    res = session.get(["ifAdminStatus.1"])
    assert len(res) == 1
    assert (
        res[0].oid
        == ".iso.org.dod.internet.mgmt.mib-2.interfaces.ifTable.ifEntry.ifAdminStatus"
    )
    assert res[0].value == "1"
    assert res[0].type == "INTEGER"
    assert res[0].index == "1"

    # With print_enums_numerically=False
    # IF-MIB::ifAdminStatus
    # up(1)
    # INTEGER
    # 1

    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_print_options_two_set_false_true_true(version):

    if version == "3" or version == 3:
        session = Session(
            version=version,
            hostname="localhost",
            port_number="11161",
            auth_protocol="SHA",
            security_level="authPriv",
            security_username="secondary_sha_aes",
            privacy_protocol="AES",
            privacy_passphrase="priv_second",
            auth_passphrase="auth_second",
            print_enums_numerically=False,
            print_full_oids=True,
            print_oids_numerically=True,
        )

        # Verify only enum option was set
        args = session.args
        assert args == (
            "-A",
            "auth_second",
            "-a",
            "SHA",
            "-X",
            "priv_second",
            "-x",
            "AES",
            "-r",
            "3",
            "-l",
            "authPriv",
            "-u",
            "secondary_sha_aes",
            "-t",
            "1",
            "-v",
            "3",
            "-O",
            "f",
            "-O",
            "n",
            "localhost:11161",
        )

    else:
        session = Session(
            hostname="localhost:11161",
            version=version,
            print_enums_numerically=False,
            print_full_oids=True,
            print_oids_numerically=True,
        )

        # Verify only enum option was set
        args = session.args
        assert args == (
            "-c",
            "public",
            "-r",
            "3",
            "-t",
            "1",
            "-v",
            "2c" if version == 2 else f"{version}",
            "-O",
            "f",
            "-O",
            "n",
            "localhost:11161",
        )

    # Verify session can do snmpget
    res = session.get(["ifAdminStatus.1"])
    assert len(res) == 1
    assert res[0].oid == ".1.3.6.1.2.1.2.2.1.7"
    assert res[0].value == "up(1)"
    assert res[0].type == "INTEGER"
    assert res[0].index == "1"

    # With print_enums_numerically=False
    # IF-MIB::ifAdminStatus
    # up(1)
    # INTEGER
    # 1

    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_print_options_two_set_true_false_true(version):

    if version == "3" or version == 3:
        session = Session(
            version=version,
            hostname="localhost",
            port_number="11161",
            auth_protocol="SHA",
            security_level="authPriv",
            security_username="secondary_sha_aes",
            privacy_protocol="AES",
            privacy_passphrase="priv_second",
            auth_passphrase="auth_second",
            print_enums_numerically=True,
            print_full_oids=False,
            print_oids_numerically=True,
        )

        # Verify only enum option was set
        args = session.args
        assert args == (
            "-A",
            "auth_second",
            "-a",
            "SHA",
            "-X",
            "priv_second",
            "-x",
            "AES",
            "-r",
            "3",
            "-l",
            "authPriv",
            "-u",
            "secondary_sha_aes",
            "-t",
            "1",
            "-v",
            "3",
            "-O",
            "e",
            "-O",
            "n",
            "localhost:11161",
        )

    else:
        session = Session(
            hostname="localhost:11161",
            version=version,
            print_enums_numerically=True,
            print_full_oids=False,
            print_oids_numerically=True,
        )

        # Verify only enum option was set
        args = session.args
        assert args == (
            "-c",
            "public",
            "-r",
            "3",
            "-t",
            "1",
            "-v",
            "2c" if version == 2 else f"{version}",
            "-O",
            "e",
            "-O",
            "n",
            "localhost:11161",
        )

    # Verify session can do snmpget
    res = session.get(["ifAdminStatus.1"])
    assert len(res) == 1
    assert res[0].oid == ".1.3.6.1.2.1.2.2.1.7"
    assert res[0].value == "1"
    assert res[0].type == "INTEGER"
    assert res[0].index == "1"

    # With print_enums_numerically=False
    # IF-MIB::ifAdminStatus
    # up(1)
    # INTEGER
    # 1

    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_print_timeticks_numerically_set(version):
    if version == "3" or version == 3:
        session = Session(
            version=version,
            hostname="localhost",
            port_number="11161",
            auth_protocol="SHA",
            security_level="authPriv",
            security_username="secondary_sha_aes",
            privacy_protocol="AES",
            privacy_passphrase="priv_second",
            auth_passphrase="auth_second",
            print_timeticks_numerically=True,
        )

        args = session.args

        assert args == (
            "-A",
            "auth_second",
            "-a",
            "SHA",
            "-X",
            "priv_second",
            "-x",
            "AES",
            "-r",
            "3",
            "-l",
            "authPriv",
            "-u",
            "secondary_sha_aes",
            "-t",
            "1",
            "-v",
            "3",
            "-O",
            "t",
            "localhost:11161",
        )

    else:
        session = Session(
            hostname="localhost:11161",
            version=version,
            print_timeticks_numerically=True,
        )

        args = session.args

        assert args == (
            "-c",
            "public",
            "-r",
            "3",
            "-t",
            "1",
            "-v",
            "2c" if version == 2 else f"{version}",
            "-O",
            "t",
            "localhost:11161",
        )

    # Test a Timeticks OID to check numeric output
    res_ticks = session.get(["sysUpTime.0"])
    assert len(res_ticks) == 1
    assert res_ticks[0].type == "Timeticks"
    # Should be a numeric string if -O t is set
    assert res_ticks[0].value.isdigit()

    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_print_timeticks_numerically_unset(version):
    if version == "3" or version == 3:
        session = Session(
            version=version,
            hostname="localhost",
            port_number="11161",
            auth_protocol="SHA",
            security_level="authPriv",
            security_username="secondary_sha_aes",
            privacy_protocol="AES",
            privacy_passphrase="priv_second",
            auth_passphrase="auth_second",
        )

        args = session.args

        assert args == (
            "-A",
            "auth_second",
            "-a",
            "SHA",
            "-X",
            "priv_second",
            "-x",
            "AES",
            "-r",
            "3",
            "-l",
            "authPriv",
            "-u",
            "secondary_sha_aes",
            "-t",
            "1",
            "-v",
            "3",
            "localhost:11161",
        )

    else:
        session = Session(
            hostname="localhost:11161",
            version=version,
        )

        args = session.args

        assert args == (
            "-c",
            "public",
            "-r",
            "3",
            "-t",
            "1",
            "-v",
            "2c" if version == 2 else f"{version}",
            "localhost:11161",
        )

    # Test a Timeticks OID to check numeric output
    res_ticks = session.get(["sysUpTime.0"])
    assert len(res_ticks) == 1
    assert res_ticks[0].type == "Timeticks"
    # Should NOT be a numeric string if -O t is not set
    assert not res_ticks[0].value.isdigit()

    del session


@pytest.mark.parametrize("version", ["1", "2c", "3", 1, 2, 3])
def test_session_print_hex_strings_set(version):
    if version == "3" or version == 3:
        session = Session(
            version=version,
            hostname="localhost",
            port_number="11161",
            auth_protocol="SHA",
            security_level="authPriv",
            security_username="secondary_sha_aes",
            privacy_protocol="AES",
            privacy_passphrase="priv_second",
            auth_passphrase="auth_second",
            print_hex_strings=True,
        )

        args = session.args

        assert args == (
            "-A",
            "auth_second",
            "-a",
            "SHA",
            "-X",
            "priv_second",
            "-x",
            "AES",
            "-r",
            "3",
            "-l",
            "authPriv",
            "-u",
            "secondary_sha_aes",
            "-t",
            "1",
            "-v",
            "3",
            "-O",
            "x",
            "localhost:11161",
        )

    else:
        session = Session(
            hostname="localhost:11161",
            version=version,
            print_hex_strings=True,
        )

        args = session.args

        assert args == (
            "-c",
            "public",
            "-r",
            "3",
            "-t",
            "1",
            "-v",
            "2c" if version == 2 else f"{version}",
            "-O",
            "x",
            "localhost:11161",
        )

    del session


def test_session_new_output_input_mib_cli_args():
    session = Session(
        hostname="localhost:11161",
        version="2c",
        print_oid_suffix_only=True,
        print_ascii_strings=True,
        output_precision="%.3f",
        regex_oid_matching=True,
        oid_suffix=".0",
        oid_prefix=".1.3",
        mib_allow_underline=True,
        mib_replace_with_latest=True,
    )

    assert session.args == (
        "-c",
        "public",
        "-r",
        "3",
        "-t",
        "1",
        "-v",
        "2c",
        "-O",
        "s",
        "-O",
        "a",
        "-Op",
        "%.3f",
        "-I",
        "b",
        "-Is",
        ".0",
        "-IS",
        ".1.3",
        "-P",
        "u",
        "-P",
        "R",
        "localhost:11161",
    )

    del session


def test_session_app_c_flags_constructor_and_to_dict():
    session = Session(
        hostname="localhost:11161",
        version="2c",
        non_repeaters=2,
        walk_dont_check_lexicographic=True,
        walk_include_requested=True,
        walk_dont_get_requested=True,
        walk_end_oid="1.3.6.1.2.1.2",
        dont_fix_pdus=True,
    )

    assert session.non_repeaters == "2"
    assert session.walk_dont_check_lexicographic is True
    assert session.walk_include_requested is True
    assert session.walk_dont_get_requested is True
    assert session.walk_end_oid == "1.3.6.1.2.1.2"
    assert session.dont_fix_pdus is True

    # Default args (SnmpOperation::All) include all configured -C flags
    assert session.args == (
        "-c",
        "public",
        "-r",
        "3",
        "-t",
        "1",
        "-v",
        "2c",
        "-Cn2",
        "-Cc",
        "-Ci",
        "-CI",
        "-CE",
        "1.3.6.1.2.1.2",
        "-Cf",
        "localhost:11161",
    )

    session_dict = session.to_dict()
    assert session_dict["non_repeaters"] == "2"
    assert session_dict["walk_dont_check_lexicographic"] is True
    assert session_dict["walk_include_requested"] is True
    assert session_dict["walk_dont_get_requested"] is True
    assert session_dict["walk_end_oid"] == "1.3.6.1.2.1.2"
    assert session_dict["dont_fix_pdus"] is True

    del session
