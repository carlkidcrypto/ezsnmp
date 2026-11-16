from .sessionbase import SessionBase
from .exceptions import _handle_error, GenericError
from typing import Union


class Session(SessionBase):
    """
    Python wrapper class for SessionBase, providing a Pythonic interface
    for managing Net-SNMP sessions.

    Supports SNMP v1, v2c, and v3. Wraps the underlying C++ ``SessionBase``
    class generated via SWIG. Use as a context manager (``with`` statement)
    to ensure the session is closed and resources are released automatically.

    Supported operations:

    - :meth:`get` — SNMP GET
    - :meth:`get_next` — SNMP GETNEXT
    - :meth:`walk` — SNMP WALK
    - :meth:`bulk_get` — SNMP GETBULK (v2c/v3 only)
    - :meth:`bulk_walk` — SNMP bulk WALK (v2c/v3 only)
    - :meth:`set` — SNMP SET

    Example::

        from ezsnmp import Session

        with Session(hostname='localhost', community='public', version=2) as session:
            results = session.get(['sysDescr.0', 'sysLocation.0'])
            for item in results:
                print(item.oid, item.value)
    """

    def __init__(
        self,
        hostname: str = "localhost",
        port_number: Union[str, int] = "",
        version: Union[str, int] = "3",
        community: str = "public",
        auth_protocol: str = "",
        auth_passphrase: str = "",
        security_engine_id: str = "",
        context_engine_id: str = "",
        security_level: str = "",
        context: str = "",
        security_username: str = "",
        privacy_protocol: str = "",
        privacy_passphrase: str = "",
        boots_time: str = "",
        retries: Union[str, int] = "3",
        timeout: Union[str, int] = "1",
        load_mibs: str = "",
        mib_directories: str = "",
        print_enums_numerically: bool = False,
        print_full_oids: bool = False,
        print_oids_numerically: bool = False,
        print_timeticks_numerically: bool = False,
        print_hex_strings: bool = False,
        set_max_repeaters_to_num: Union[str, int] = "10",
        print_oid_suffix_only: bool = False,
        print_oid_module_name: bool = False,
        print_oid_ucd_style: bool = False,
        print_ascii_strings: bool = False,
        print_leading_zero_hex: bool = False,
        print_hex_text: bool = False,
        dont_breakdown_oids: bool = False,
        escape_quotes_in_indexes: bool = False,
        extended_index_format: bool = False,
        dont_print_units: bool = False,
        output_precision: str = "",
        regex_oid_matching: bool = False,
        ignore_display_hints: bool = False,
        dont_check_range: bool = False,
        random_access_oid: bool = False,
        read_ucd_style_oid: bool = False,
        oid_suffix: str = "",
        oid_prefix: str = "",
        mib_allow_underline: bool = False,
        mib_comment_to_eol: bool = False,
        mib_replace_with_latest: bool = False,
        non_repeaters: Union[str, int] = "",
        walk_dont_check_lexicographic: bool = False,
        walk_include_requested: bool = False,
        walk_dont_get_requested: bool = False,
        walk_end_oid: str = "",
        dont_fix_pdus: bool = False,
    ):
        """Initialize the Session object with NetSNMP session parameters.

        :param hostname: The hostname or IP address of the SNMP agent.
        :type hostname: str
        :param port_number: The port number of the SNMP agent.
        :type port_number: Union[str, int]
        :param version: The SNMP version to use. All of the following forms are
            accepted and equivalent for SNMPv2c:

            - Integer ``2`` — automatically converted to ``"2c"`` internally.
            - String ``"2"`` — passed through as-is; net-snmp accepts ``-v 2``.
            - String ``"2c"`` — the canonical form; passed through as-is.

            For other versions use ``1`` / ``"1"`` (SNMPv1) or ``3`` / ``"3"``
            (SNMPv3).
        :type version: Union[str, int]
        :param community: The community string for SNMPv1/v2c.
        :type community: str
        :param auth_protocol: The authentication protocol (e.g., "MD5", "SHA").
        :type auth_protocol: str
        :param auth_passphrase: The authentication passphrase.
        :type auth_passphrase: str
        :param security_engine_id: The security engine ID.
        :type security_engine_id: str
        :param context_engine_id: The context engine ID.
        :type context_engine_id: str
        :param security_level: The security level (e.g., "noAuthNoPriv", "authNoPriv", "authPriv").
        :type security_level: str
        :param context: The SNMPv3 context name used to identify a collection of management information (SNMPv3 only).
        :type context: str
        :param security_username: The security username.
        :type security_username: str
        :param privacy_protocol: The privacy protocol (e.g., "DES", "AES").
        :type privacy_protocol: str
        :param privacy_passphrase: The privacy passphrase.
        :type privacy_passphrase: str
        :param boots_time: The SNMPv3 authoritative engine boots and time, formatted
            as "BOOTS,TIME" (e.g., "1,100"). Used to synchronize with the agent's
            time window.
        :type boots_time: str
        :param retries: The number of retries.
        :type retries: Union[str, int]
        :param timeout: The timeout value in seconds.
        :type timeout: Union[str, int]
        :param load_mibs: Comma-separated string of MIB modules to load.
        :type load_mibs: str
        :param mib_directories: Comma-separated string of directories to search for MIB files.
        :type mib_directories: str
        :param print_enums_numerically: Whether to print enums numerically.
        :type print_enums_numerically: bool
        :param print_full_oids: Whether to print full OIDs.
        :type print_full_oids: bool
        :param print_oids_numerically: Whether to print OIDs numerically.
        :type print_oids_numerically: bool
        :param print_timeticks_numerically: Whether to print timeticks numerically.
        :type print_timeticks_numerically: bool
        :param print_hex_strings: Whether to print OCTET STRING values in hex format.
        :type print_hex_strings: bool
        :param set_max_repeaters_to_num: The maximum number of repeaters for GETBULK PDUs. Defaults to 10. Only applies to :meth:`bulk_get` and :meth:`bulk_walk`.
        :type set_max_repeaters_to_num: Union[str, int]
        :param print_oid_suffix_only: Whether to print only the last symbolic element of OIDs (``-O s``).
        :type print_oid_suffix_only: bool
        :param print_oid_module_name: Whether to print module name plus last symbolic element of OIDs (``-O S``).
        :type print_oid_module_name: bool
        :param print_oid_ucd_style: Whether to print OIDs in UCD-style (``-O u``).
        :type print_oid_ucd_style: bool
        :param print_ascii_strings: Whether to print all strings as ASCII (``-O a``).
        :type print_ascii_strings: bool
        :param print_leading_zero_hex: Whether to print leading zeroes in hex strings (``-O 0``).
        :type print_leading_zero_hex: bool
        :param print_hex_text: Whether to print ASCII text alongside hex output (``-O T``).
        :type print_hex_text: bool
        :param dont_breakdown_oids: Whether to disable OID index breakdown (``-O b``).
        :type dont_breakdown_oids: bool
        :param escape_quotes_in_indexes: Whether to escape quotes in string indexes (``-O E``).
        :type escape_quotes_in_indexes: bool
        :param extended_index_format: Whether to print indexes in bracketed extended format (``-O X``).
        :type extended_index_format: bool
        :param dont_print_units: Whether to suppress MIB units in output (``-O U``).
        :type dont_print_units: bool
        :param output_precision: Precision format string for float/double output (``-O p``).
        :type output_precision: str
        :param regex_oid_matching: Whether to enable regex OID matching (``-I b``).
        :type regex_oid_matching: bool
        :param ignore_display_hints: Whether to ignore MIB DISPLAY-HINTs on input (``-I h``).
        :type ignore_display_hints: bool
        :param dont_check_range: Whether to disable range checks on input values (``-I r``).
        :type dont_check_range: bool
        :param random_access_oid: Whether to enable random-access OID lookup (``-I R``).
        :type random_access_oid: bool
        :param read_ucd_style_oid: Whether to read OIDs relative to UCD default prefix (``-I u``).
        :type read_ucd_style_oid: bool
        :param oid_suffix: Suffix to append to input OIDs (``-I s``).
        :type oid_suffix: str
        :param oid_prefix: Prefix to prepend to input OIDs (``-I S``).
        :type oid_prefix: str
        :param mib_allow_underline: Whether to allow underscores in MIB labels (``-P u``).
        :type mib_allow_underline: bool
        :param mib_comment_to_eol: Whether to treat ``--`` MIB comments as extending to end-of-line (``-P c``).
        :type mib_comment_to_eol: bool
        :param mib_replace_with_latest: Whether to replace duplicate MIB objects with latest definition (``-P R``).
        :type mib_replace_with_latest: bool
        :param non_repeaters: Number of non-repeaters for GETBULK PDUs (``-C n``). Only applies to :meth:`bulk_get` and :meth:`bulk_walk`.
        :type non_repeaters: Union[str, int]
        :param walk_dont_check_lexicographic: Whether to disable lexicographical OID ordering checks during walks (``-C c``).
        :type walk_dont_check_lexicographic: bool
        :param walk_include_requested: Whether to include the requested OID in walk results (``-C i``).
        :type walk_include_requested: bool
        :param walk_dont_get_requested: Whether to skip GET fallback when walk returns nothing (``-C I``).
        :type walk_dont_get_requested: bool
        :param walk_end_oid: OID at which to stop walking (``-C E``).
        :type walk_end_oid: str
        :param dont_fix_pdus: Whether to disable PDU error fixing on GET/GETNEXT (``-C f``).
        :type dont_fix_pdus: bool

        """

        # Note that underlying SessionBase object depends on all parameters to be strings.
        # This is the case, since at the end of the day we are building a command line string
        # to pass to the NetSNMP command line tool.
        try:

            temp_version = ""
            if version == 2:
                temp_version = "2c"
            else:
                temp_version = str(version)

            # Initialize the SWIG-wrapped C++ SessionBase via super().__init__().
            # This ensures that calling inherited methods like _get_context() directly
            # on the Session object works correctly (fixes GitHub issue #656).
            super().__init__(
                hostname,
                str(port_number),
                temp_version,
                community,
                auth_protocol,
                auth_passphrase,
                security_engine_id,
                context_engine_id,
                security_level,
                context,
                security_username,
                privacy_protocol,
                privacy_passphrase,
                boots_time,
                str(retries),
                str(timeout),
                load_mibs,
                mib_directories,
                print_enums_numerically,
                print_full_oids,
                print_oids_numerically,
                print_timeticks_numerically,
                print_hex_strings,
                "",  # Set to empty string here. We will set it in the bulk methods.
                print_oid_suffix_only,
                print_oid_module_name,
                print_oid_ucd_style,
                print_ascii_strings,
                print_leading_zero_hex,
                print_hex_text,
                dont_breakdown_oids,
                escape_quotes_in_indexes,
                extended_index_format,
                dont_print_units,
                output_precision,
                regex_oid_matching,
                ignore_display_hints,
                dont_check_range,
                random_access_oid,
                read_ucd_style_oid,
                oid_suffix,
                oid_prefix,
                mib_allow_underline,
                mib_comment_to_eol,
                mib_replace_with_latest,
                str(non_repeaters),
                walk_dont_check_lexicographic,
                walk_include_requested,
                walk_dont_get_requested,
                walk_end_oid,
                dont_fix_pdus,
            )

            # Track the closed state for __del__ and multiple closes
            self._closed = False
            self.__set_max_repeaters_to_num = str(set_max_repeaters_to_num)

        except Exception as e:
            _handle_error(e)

    def __enter__(self):
        """Enter the context manager, returning the session object."""
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the context manager, automatically closing the session."""
        self.close()
        return None

    def __del__(self):
        """
        Finalizer: A last-ditch effort to call .close() when the object
        is garbage collected, preventing resource leaks.
        """

        if hasattr(self, "_closed") and not self._closed:
            try:
                self.close()
            except Exception:
                # Must not raise exceptions in __del__
                pass

    @property
    def args(self):
        """Get the tuple of arguments used for NetSNMP commands.

        :type: tuple
        """
        return super()._get_args()

    @property
    def hostname(self):
        """Get the hostname or IP address of the SNMP agent.

        :type: str
        """
        return super()._get_hostname()

    @hostname.setter
    def hostname(self, value):
        """Set the hostname or IP address of the SNMP agent.

        :param value: The hostname or IP address to set.
        :type value: str
        """
        super()._set_hostname(value)

    @property
    def port_number(self):
        """Get the port number of the SNMP agent.

        :type: str
        """
        return super()._get_port_number()

    @port_number.setter
    def port_number(self, value):
        """Set the port number of the SNMP agent.

        :param value: The port number to set.
        :type value: str
        """
        super()._set_port_number(value)

    @property
    def version(self):
        """Get the SNMP version being used.

        :type: str
        """
        return super()._get_version()

    @version.setter
    def version(self, value):
        """Set the SNMP version to use.

        :param value: The SNMP version to set (1, 2c, or 3).
        :type value: str
        """
        super()._set_version(value)

    @property
    def community(self):
        """Get the community string for SNMPv1/v2c.

        :type: str
        """
        return super()._get_community()

    @community.setter
    def community(self, value):
        """Set the community string for SNMPv1/v2c.

        :param value: The community string to set.
        :type value: str
        """
        super()._set_community(value)

    @property
    def auth_protocol(self):
        """Get the authentication protocol.

        :type: str
        """
        return super()._get_auth_protocol()

    @auth_protocol.setter
    def auth_protocol(self, value):
        """Set the authentication protocol.

        :param value: The authentication protocol to set (e.g., "MD5", "SHA").
        :type value: str
        """
        super()._set_auth_protocol(value)

    @property
    def auth_passphrase(self):
        """Get the authentication passphrase.

        :type: str
        """
        return super()._get_auth_passphrase()

    @auth_passphrase.setter
    def auth_passphrase(self, value):
        """Set the authentication passphrase.

        :param value: The authentication passphrase to set.
        :type value: str
        """
        super()._set_auth_passphrase(value)

    @property
    def security_engine_id(self):
        """Get the security engine ID.

        :type: str
        """
        return super()._get_security_engine_id()

    @security_engine_id.setter
    def security_engine_id(self, value):
        """Set the security engine ID.

        :param value: The security engine ID to set.
        :type value: str
        """
        super()._set_security_engine_id(value)

    @property
    def context_engine_id(self):
        """Get the context engine ID.

        :type: str
        """
        return super()._get_context_engine_id()

    @context_engine_id.setter
    def context_engine_id(self, value):
        """Set the context engine ID.

        :param value: The context engine ID to set.
        :type value: str
        """
        super()._set_context_engine_id(value)

    @property
    def security_level(self):
        """Get the security level.

        :type: str
        """
        return super()._get_security_level()

    @security_level.setter
    def security_level(self, value):
        """Set the security level.

        :param value: The security level to set (e.g., "noAuthNoPriv", "authNoPriv", "authPriv").
        :type value: str
        """
        super()._set_security_level(value)

    @property
    def context(self):
        """Get the SNMPv3 context name.

        :type: str
        """
        return super()._get_context()

    @context.setter
    def context(self, value):
        """Set the SNMPv3 context name.

        :param value: The SNMPv3 context name to set.
        :type value: str
        """
        super()._set_context(value)

    @property
    def security_username(self):
        """Get the security username.

        :type: str
        """
        return super()._get_security_username()

    @security_username.setter
    def security_username(self, value):
        """Set the security username.

        :param value: The security username to set.
        :type value: str
        """
        super()._set_security_username(value)

    @property
    def privacy_protocol(self):
        """Get the privacy protocol.

        :type: str
        """
        return super()._get_privacy_protocol()

    @privacy_protocol.setter
    def privacy_protocol(self, value):
        """Set the privacy protocol.

        :param value: The privacy protocol to set (e.g., "DES", "AES").
        :type value: str
        """
        super()._set_privacy_protocol(value)

    @property
    def privacy_passphrase(self):
        """Get the privacy passphrase.

        :type: str
        """
        return super()._get_privacy_passphrase()

    @privacy_passphrase.setter
    def privacy_passphrase(self, value):
        """Set the privacy passphrase.

        :param value: The privacy passphrase to set.
        :type value: str
        """
        super()._set_privacy_passphrase(value)

    @property
    def boots_time(self):
        """Get the boots time.

        :type: str
        """
        return super()._get_boots_time()

    @boots_time.setter
    def boots_time(self, value):
        """Set the SNMPv3 authoritative engine boots and time.

        :param value: The boots and time string, formatted as "BOOTS,TIME"
            (e.g., "1,100"). Used to synchronize with the agent's time window.
        :type value: str
        """
        super()._set_boots_time(value)

    @property
    def retries(self):
        """Get the number of retries.

        :type: str
        """
        return super()._get_retries()

    @retries.setter
    def retries(self, value):
        """Set the number of retries.

        :param value: The number of retries to set.
        :type value: Union[str, int]
        """
        super()._set_retries(value)

    @property
    def timeout(self):
        """Get the timeout value.

        :type: str
        """
        return super()._get_timeout()

    @timeout.setter
    def timeout(self, value):
        """Set the timeout value.

        :param value: The timeout value to set in seconds.
        :type value: Union[str, int]
        """
        super()._set_timeout(value)

    @property
    def load_mibs(self):
        """Get the list of MIBs to load.

        :type: str
        """
        return super()._get_load_mibs()

    @load_mibs.setter
    def load_mibs(self, value):
        """Set the list of MIBs to load.

        :param value: The new list of MIBs to load.
        :type value: str
        """
        super()._set_load_mibs(value)

    @property
    def mib_directories(self):
        """Get the directories to search for MIBs.

        :type: str
        """
        return super()._get_mib_directories()

    @mib_directories.setter
    def mib_directories(self, value):
        """Set the directories to search for MIBs.

        :param value: The new directories to search for MIBs.
        :type value: str
        """
        super()._set_mib_directories(value)

    @property
    def print_enums_numerically(self):
        """Get whether to print enums numerically.

        :type: bool
        """
        return super()._get_print_enums_numerically()

    @print_enums_numerically.setter
    def print_enums_numerically(self, value):
        """Set whether to print enums numerically.

        :param value: The new value for printing enums numerically.
        :type value: bool
        """
        super()._set_print_enums_numerically(value)

    @property
    def print_full_oids(self):
        """Get whether to print full OIDs.

        :type: bool
        """
        return super()._get_print_full_oids()

    @print_full_oids.setter
    def print_full_oids(self, value):
        """Set whether to print full OIDs.

        :param value: The new value for printing full OIDs.
        :type value: bool
        """
        super()._set_print_full_oids(value)

    @property
    def print_oids_numerically(self):
        """Get whether to print OIDs numerically.

        :type: bool
        """
        return super()._get_print_oids_numerically()

    @print_oids_numerically.setter
    def print_oids_numerically(self, value):
        """Set whether to print OIDs numerically.

        :param value: The new value for printing OIDs numerically.
        :type value: bool
        """
        super()._set_print_oids_numerically(value)

    @property
    def print_timeticks_numerically(self):
        """Get whether to print timeticks numerically.

        :type: bool
        """
        return super()._get_print_timeticks_numerically()

    @print_timeticks_numerically.setter
    def print_timeticks_numerically(self, value):
        """Set whether to print timeticks numerically.

        :param value: The new value for printing timeticks numerically.
        :type value: bool
        """
        super()._set_print_timeticks_numerically(value)

    @property
    def print_hex_strings(self):
        """Get whether to print OCTET STRING values as hex strings.

        :type: bool
        """
        return super()._get_print_hex_strings()

    @print_hex_strings.setter
    def print_hex_strings(self, value):
        """Set whether to print OCTET STRING values as hex strings.

        :param value: The new value for printing OCTET STRING values as hex strings.
        :type value: bool
        """
        super()._set_print_hex_strings(value)

    @property
    def set_max_repeaters_to_num(self):
        """Get the maximum number of repeaters for GETBULK PDUs.

        :type: str
        """
        return super()._get_set_max_repeaters_to_num()

    @set_max_repeaters_to_num.setter
    def set_max_repeaters_to_num(self, value):
        """Set the maximum number of repeaters for GETBULK PDUs.

        :param value: The maximum number of repeaters. Only applies to bulk_walk
            and bulk_get operations.
        :type value: Union[str, int]
        """
        super()._set_max_repeaters_to_num(value)

    @property
    def print_oid_suffix_only(self):
        """Get whether to print only the last symbolic element of OIDs.

        :type: bool
        """
        return super()._get_print_oid_suffix_only()

    @print_oid_suffix_only.setter
    def print_oid_suffix_only(self, value):
        """Set whether to print only the last symbolic element of OIDs.

        :param value: The new value for printing OID suffix only.
        :type value: bool
        """
        super()._set_print_oid_suffix_only(value)

    @property
    def print_oid_module_name(self):
        """Get whether to print module name plus last symbolic element of OIDs.

        :type: bool
        """
        return super()._get_print_oid_module_name()

    @print_oid_module_name.setter
    def print_oid_module_name(self, value):
        """Set whether to print module name plus last symbolic element of OIDs.

        :param value: The new value for printing OID module name.
        :type value: bool
        """
        super()._set_print_oid_module_name(value)

    @property
    def print_oid_ucd_style(self):
        """Get whether to print OIDs in UCD-style.

        :type: bool
        """
        return super()._get_print_oid_ucd_style()

    @print_oid_ucd_style.setter
    def print_oid_ucd_style(self, value):
        """Set whether to print OIDs in UCD-style.

        :param value: The new value for printing OIDs in UCD-style.
        :type value: bool
        """
        super()._set_print_oid_ucd_style(value)

    @property
    def print_ascii_strings(self):
        """Get whether to print all strings as ASCII.

        :type: bool
        """
        return super()._get_print_ascii_strings()

    @print_ascii_strings.setter
    def print_ascii_strings(self, value):
        """Set whether to print all strings as ASCII.

        :param value: The new value for printing ASCII strings.
        :type value: bool
        """
        super()._set_print_ascii_strings(value)

    @property
    def print_leading_zero_hex(self):
        """Get whether to print leading zeroes in hex strings.

        :type: bool
        """
        return super()._get_print_leading_zero_hex()

    @print_leading_zero_hex.setter
    def print_leading_zero_hex(self, value):
        """Set whether to print leading zeroes in hex strings.

        :param value: The new value for printing leading zeroes in hex strings.
        :type value: bool
        """
        super()._set_print_leading_zero_hex(value)

    @property
    def print_hex_text(self):
        """Get whether to print ASCII text alongside hex output.

        :type: bool
        """
        return super()._get_print_hex_text()

    @print_hex_text.setter
    def print_hex_text(self, value):
        """Set whether to print ASCII text alongside hex output.

        :param value: The new value for printing hex text.
        :type value: bool
        """
        super()._set_print_hex_text(value)

    @property
    def dont_breakdown_oids(self):
        """Get whether to disable OID index breakdown.

        :type: bool
        """
        return super()._get_dont_breakdown_oids()

    @dont_breakdown_oids.setter
    def dont_breakdown_oids(self, value):
        """Set whether to disable OID index breakdown.

        :param value: The new value for disabling OID index breakdown.
        :type value: bool
        """
        super()._set_dont_breakdown_oids(value)

    @property
    def escape_quotes_in_indexes(self):
        """Get whether to escape quotes in string indexes.

        :type: bool
        """
        return super()._get_escape_quotes_in_indexes()

    @escape_quotes_in_indexes.setter
    def escape_quotes_in_indexes(self, value):
        """Set whether to escape quotes in string indexes.

        :param value: The new value for escaping quotes in string indexes.
        :type value: bool
        """
        super()._set_escape_quotes_in_indexes(value)

    @property
    def extended_index_format(self):
        """Get whether to print indexes in bracketed extended format.

        :type: bool
        """
        return super()._get_extended_index_format()

    @extended_index_format.setter
    def extended_index_format(self, value):
        """Set whether to print indexes in bracketed extended format.

        :param value: The new value for extended index format.
        :type value: bool
        """
        super()._set_extended_index_format(value)

    @property
    def dont_print_units(self):
        """Get whether to suppress MIB units in output.

        :type: bool
        """
        return super()._get_dont_print_units()

    @dont_print_units.setter
    def dont_print_units(self, value):
        """Set whether to suppress MIB units in output.

        :param value: The new value for suppressing MIB units.
        :type value: bool
        """
        super()._set_dont_print_units(value)

    @property
    def output_precision(self):
        """Get the precision format string for float/double output.

        :type: str
        """
        return super()._get_output_precision()

    @output_precision.setter
    def output_precision(self, value):
        """Set the precision format string for float/double output.

        :param value: The precision format string.
        :type value: str
        """
        super()._set_output_precision(value)

    @property
    def regex_oid_matching(self):
        """Get whether to enable regex OID matching.

        :type: bool
        """
        return super()._get_regex_oid_matching()

    @regex_oid_matching.setter
    def regex_oid_matching(self, value):
        """Set whether to enable regex OID matching.

        :param value: The new value for regex OID matching.
        :type value: bool
        """
        super()._set_regex_oid_matching(value)

    @property
    def ignore_display_hints(self):
        """Get whether to ignore MIB DISPLAY-HINTs on input.

        :type: bool
        """
        return super()._get_ignore_display_hints()

    @ignore_display_hints.setter
    def ignore_display_hints(self, value):
        """Set whether to ignore MIB DISPLAY-HINTs on input.

        :param value: The new value for ignoring display hints.
        :type value: bool
        """
        super()._set_ignore_display_hints(value)

    @property
    def dont_check_range(self):
        """Get whether to disable range checks on input values.

        :type: bool
        """
        return super()._get_dont_check_range()

    @dont_check_range.setter
    def dont_check_range(self, value):
        """Set whether to disable range checks on input values.

        :param value: The new value for disabling range checks.
        :type value: bool
        """
        super()._set_dont_check_range(value)

    @property
    def random_access_oid(self):
        """Get whether to enable random-access OID lookup.

        :type: bool
        """
        return super()._get_random_access_oid()

    @random_access_oid.setter
    def random_access_oid(self, value):
        """Set whether to enable random-access OID lookup.

        :param value: The new value for random-access OID lookup.
        :type value: bool
        """
        super()._set_random_access_oid(value)

    @property
    def read_ucd_style_oid(self):
        """Get whether to read OIDs relative to UCD default prefix.

        :type: bool
        """
        return super()._get_read_ucd_style_oid()

    @read_ucd_style_oid.setter
    def read_ucd_style_oid(self, value):
        """Set whether to read OIDs relative to UCD default prefix.

        :param value: The new value for reading UCD-style OIDs.
        :type value: bool
        """
        super()._set_read_ucd_style_oid(value)

    @property
    def oid_suffix(self):
        """Get the suffix to append to input OIDs.

        :type: str
        """
        return super()._get_oid_suffix()

    @oid_suffix.setter
    def oid_suffix(self, value):
        """Set the suffix to append to input OIDs.

        :param value: The OID suffix to set.
        :type value: str
        """
        super()._set_oid_suffix(value)

    @property
    def oid_prefix(self):
        """Get the prefix to prepend to input OIDs.

        :type: str
        """
        return super()._get_oid_prefix()

    @oid_prefix.setter
    def oid_prefix(self, value):
        """Set the prefix to prepend to input OIDs.

        :param value: The OID prefix to set.
        :type value: str
        """
        super()._set_oid_prefix(value)

    @property
    def mib_allow_underline(self):
        """Get whether to allow underscores in MIB labels.

        :type: bool
        """
        return super()._get_mib_allow_underline()

    @mib_allow_underline.setter
    def mib_allow_underline(self, value):
        """Set whether to allow underscores in MIB labels.

        :param value: The new value for allowing underscores in MIB labels.
        :type value: bool
        """
        super()._set_mib_allow_underline(value)

    @property
    def mib_comment_to_eol(self):
        """Get whether to treat ``--`` MIB comments as extending to end-of-line.

        :type: bool
        """
        return super()._get_mib_comment_to_eol()

    @mib_comment_to_eol.setter
    def mib_comment_to_eol(self, value):
        """Set whether to treat ``--`` MIB comments as extending to end-of-line.

        :param value: The new value for MIB comment to end-of-line.
        :type value: bool
        """
        super()._set_mib_comment_to_eol(value)

    @property
    def mib_replace_with_latest(self):
        """Get whether to replace duplicate MIB objects with latest definition.

        :type: bool
        """
        return super()._get_mib_replace_with_latest()

    @mib_replace_with_latest.setter
    def mib_replace_with_latest(self, value):
        """Set whether to replace duplicate MIB objects with latest definition.

        :param value: The new value for replacing duplicate MIB objects.
        :type value: bool
        """
        super()._set_mib_replace_with_latest(value)

    @property
    def non_repeaters(self):
        """Get the number of non-repeaters for GETBULK PDUs.

        :type: str
        """
        return super()._get_non_repeaters()

    @non_repeaters.setter
    def non_repeaters(self, value):
        """Set the number of non-repeaters for GETBULK PDUs.

        :param value: The number of non-repeaters. Only applies to bulk_walk
            and bulk_get operations.
        :type value: Union[str, int]
        """
        super()._set_non_repeaters(str(value))

    @property
    def walk_dont_check_lexicographic(self):
        """Get whether to disable lexicographical OID ordering checks during walks.

        :type: bool
        """
        return super()._get_walk_dont_check_lexicographic()

    @walk_dont_check_lexicographic.setter
    def walk_dont_check_lexicographic(self, value):
        """Set whether to disable lexicographical OID ordering checks during walks.

        :param value: The new value for disabling lexicographical checks.
        :type value: bool
        """
        super()._set_walk_dont_check_lexicographic(value)

    @property
    def walk_include_requested(self):
        """Get whether to include the requested OID in walk results.

        :type: bool
        """
        return super()._get_walk_include_requested()

    @walk_include_requested.setter
    def walk_include_requested(self, value):
        """Set whether to include the requested OID in walk results.

        :param value: The new value for including the requested OID.
        :type value: bool
        """
        super()._set_walk_include_requested(value)

    @property
    def walk_dont_get_requested(self):
        """Get whether to skip GET fallback when walk returns nothing.

        :type: bool
        """
        return super()._get_walk_dont_get_requested()

    @walk_dont_get_requested.setter
    def walk_dont_get_requested(self, value):
        """Set whether to skip GET fallback when walk returns nothing.

        :param value: The new value for skipping GET fallback.
        :type value: bool
        """
        super()._set_walk_dont_get_requested(value)

    @property
    def walk_end_oid(self):
        """Get the OID at which to stop walking.

        :type: str
        """
        return super()._get_walk_end_oid()

    @walk_end_oid.setter
    def walk_end_oid(self, value):
        """Set the OID at which to stop walking.

        :param value: The end OID for walk operations.
        :type value: str
        """
        super()._set_walk_end_oid(value)

    @property
    def dont_fix_pdus(self):
        """Get whether to disable PDU error fixing on GET/GETNEXT.

        :type: bool
        """
        return super()._get_dont_fix_pdus()

    @dont_fix_pdus.setter
    def dont_fix_pdus(self, value):
        """Set whether to disable PDU error fixing on GET/GETNEXT.

        :param value: The new value for disabling PDU error fixing.
        :type value: bool
        """
        super()._set_dont_fix_pdus(value)

    def close(self):
        """Close the SNMP session and release resources."""
        if not self._closed:
            self._closed = True
            try:
                self._close_session()
            except Exception as e:
                _handle_error(e)

    def _close_session(self):
        return super()._close()

    def __repr__(self):
        """Return detailed string representation for debugging."""
        return (
            f"Session(hostname={self.hostname!r}, port_number={self.port_number!r}, "
            f"version={self.version!r}, community={('***' if self.community else '')!r}, "
            f"security_username={self.security_username!r}, "
            f"retries={self.retries!r}, timeout={self.timeout!r})"
        )

    def __str__(self):
        """Return readable string representation."""
        return (
            f"SNMP Session: {self.hostname}:{self.port_number or 'default'} "
            f"(version={self.version})"
        )

    def to_dict(self):
        """Convert session to dictionary for logging/JSON serialization.

        Sensitive fields (community, passwords) are masked.

        :return: A dictionary of session parameters, with sensitive values masked.
        :rtype: dict
        """
        # Core properties that should always work
        result = {
            "hostname": self.hostname,
            "port_number": self.port_number,
            "version": self.version,
            "community": "***" if self.community else "",
            "auth_protocol": self.auth_protocol,
            "auth_passphrase": "***" if self.auth_passphrase else "",
            "security_engine_id": self.security_engine_id,
            "context_engine_id": self.context_engine_id,
            "security_level": self.security_level,
            "context": self.context,
            "security_username": self.security_username,
            "privacy_protocol": self.privacy_protocol,
            "privacy_passphrase": "***" if self.privacy_passphrase else "",
            "boots_time": self.boots_time,
            "retries": self.retries,
            "timeout": self.timeout,
        }

        # Optional properties - some may not have getters implemented in C++
        optional_props = [
            "load_mibs",
            "mib_directories",
            "print_enums_numerically",
            "print_full_oids",
            "print_oids_numerically",
            "print_timeticks_numerically",
            "print_hex_strings",
            "set_max_repeaters_to_num",
            "print_oid_suffix_only",
            "print_oid_module_name",
            "print_oid_ucd_style",
            "print_ascii_strings",
            "print_leading_zero_hex",
            "print_hex_text",
            "dont_breakdown_oids",
            "escape_quotes_in_indexes",
            "extended_index_format",
            "dont_print_units",
            "output_precision",
            "regex_oid_matching",
            "ignore_display_hints",
            "dont_check_range",
            "random_access_oid",
            "read_ucd_style_oid",
            "oid_suffix",
            "oid_prefix",
            "mib_allow_underline",
            "mib_comment_to_eol",
            "mib_replace_with_latest",
            "non_repeaters",
            "walk_dont_check_lexicographic",
            "walk_include_requested",
            "walk_dont_get_requested",
            "walk_end_oid",
            "dont_fix_pdus",
        ]

        for prop in optional_props:
            try:
                result[prop] = getattr(self, prop)
            except AttributeError:
                # Getter not implemented in SessionBase
                result[prop] = None

        return result

    def walk(self, oid="."):
        """
        Walks through the SNMP tree starting from the given OID.
        This method performs an SNMP walk operation, which retrieves a subtree of
        management values from the SNMP agent, starting from the specified OID.

        :param oid: The starting OID for the SNMP walk. Defaults to ``"."``
                which starts the walk from the top of the OID tree.
        :type oid: str

        :return: A tuple of Result objects containing SNMP variable bindings. Each Result object has
            attributes: oid (str), index (str), value (str), and type (str)
        :rtype: tuple[Result]

        :raises ConnectionError: If the exception type is `ConnectionErrorBase`.
        :raises GenericError: If the exception type is `GenericErrorBase`.
        :raises NoSuchInstanceError: If the exception type is `NoSuchInstanceErrorBase`.
        :raises NoSuchNameError: If the exception type is `NoSuchNameErrorBase`.
        :raises NoSuchObjectError: If the exception type is `NoSuchObjectErrorBase`.
        :raises PacketError: If the exception type is `PacketErrorBase`.
        :raises ParseError: If the exception type is `ParseErrorBase`.
        :raises TimeoutError: If the exception type is `TimeoutErrorBase`.
        :raises UndeterminedTypeError: If the exception type is `UndeterminedTypeErrorBase`.
        :raises UnknownObjectIDError: If the exception type is `UnknownObjectIDErrorBase`.
        :raises Exception: If the exception type does not match any of the above, the original
            exception `e` is raised.

        Example:
            >>> from ezsnmp import Session
            >>> session = Session(hostname="localhost", community="public", version="2")
            >>> results = session.walk("1.3.6.1.2.1")
            >>> for item in results:
            ...     print("OID:", item.oid)
            ...     print("Index:", item.index)
            ...     print("Value:", item.value)
            ...     print("Type:", item.type)
            ...     print("---")
        """

        try:
            return super().walk(oid)
        except Exception as e:
            _handle_error(e)

    def bulk_walk(self, oids=None):
        """
        Performs a bulk SNMP walk (GETBULK-based) operation to retrieve a collection of values.
        The bulk walk operation is designed to return multiple OIDs in a single request,
        making it more efficient than regular walk operations for retrieving large amounts of data.

        Requires SNMPv2c or SNMPv3. GETBULK is not supported in SNMPv1.

        Accepts either a single OID string or a list of OID strings.

        :param oids: A single OID string or a list of base OIDs to start the walks from.
            Defaults to ``None``, which is treated as an empty list.
        :type oids: Union[str, list[str], None]
        :return: A tuple of Result objects containing SNMP variable bindings. Each Result object has
            attributes: oid (str), index (str), value (str), and type (str)
        :rtype: tuple[Result]

        :raises ConnectionError: If the exception type is `ConnectionErrorBase`.
        :raises GenericError: If the exception type is `GenericErrorBase`.
        :raises NoSuchInstanceError: If the exception type is `NoSuchInstanceErrorBase`.
        :raises NoSuchNameError: If the exception type is `NoSuchNameErrorBase`.
        :raises NoSuchObjectError: If the exception type is `NoSuchObjectErrorBase`.
        :raises PacketError: If the exception type is `PacketErrorBase`.
        :raises ParseError: If the exception type is `ParseErrorBase`.
        :raises TimeoutError: If the exception type is `TimeoutErrorBase`.
        :raises UndeterminedTypeError: If the exception type is `UndeterminedTypeErrorBase`.
        :raises UnknownObjectIDError: If the exception type is `UnknownObjectIDErrorBase`.
        :raises Exception: If the exception type does not match any of the above, the original
            exception `e` is raised.

        Example (single OID string):
            >>> from ezsnmp import Session
            >>> session = Session(hostname="localhost", community="public", version="2")
            >>> results = session.bulk_walk("1.3.6.1.2.1")
            >>> print("OID:", results[0].oid)

        Example (list of OIDs):
            >>> results = session.bulk_walk(["1.3.6.1.2.1.1", "1.3.6.1.2.1.2"])
            >>> for item in results:
            ...     print("OID:", item.oid)
            ...     print("Index:", item.index)
            ...     print("Value:", item.value)
            ...     print("Type:", item.type)
            ...     print("---")
        """

        try:
            if oids is None:
                oids = []
            self.set_max_repeaters_to_num = self.__set_max_repeaters_to_num
            return self._bulk_walk(oids)
        except Exception as e:
            _handle_error(e)
        finally:
            self.set_max_repeaters_to_num = ""

    def _bulk_walk(self, oids):
        return super().bulk_walk(oids)

    def get(self, oids=None):
        """
        Performs an SNMP GET operation to retrieve values for one or more OIDs.

        Accepts either a single OID string or a list of OID strings.

        :param oids: A single OID string or a list of Object Identifiers (OIDs) to retrieve
            values from. Defaults to ``None``, which is treated as an empty list.
        :type oids: Union[str, list[str], None]
        :return: A tuple of Result objects containing SNMP variable bindings with attributes:
            oid (str), index (str), value (str), and type (str)
        :rtype: tuple[Result]

        :raises GenericError: If the exception type is `GenericErrorBase`.
        :raises ConnectionError: If the exception type is `ConnectionErrorBase`.
        :raises NoSuchInstanceError: If the exception type is `NoSuchInstanceErrorBase`.
        :raises NoSuchNameError: If the exception type is `NoSuchNameErrorBase`.
        :raises NoSuchObjectError: If the exception type is `NoSuchObjectErrorBase`.
        :raises PacketError: If the exception type is `PacketErrorBase`.
        :raises ParseError: If the exception type is `ParseErrorBase`.
        :raises TimeoutError: If the exception type is `TimeoutErrorBase`.
        :raises UndeterminedTypeError: If the exception type is `UndeterminedTypeErrorBase`.
        :raises UnknownObjectIDError: If the exception type is `UnknownObjectIDErrorBase`.
        :raises Exception: If the exception type does not match any of the above, the original
            exception `e` is raised.

        Example (single OID string):
            >>> from ezsnmp import Session
            >>> session = Session(hostname="localhost", community="public", version="2")
            >>> result = session.get("1.3.6.1.2.1.1.1.0")
            >>> print("OID:", result[0].oid)

        Example (list of OIDs):
            >>> results = session.get(["1.3.6.1.2.1.1.1.0", "1.3.6.1.2.1.1.2.0"])
            >>> for item in results:
            ...     print("OID:", item.oid)
            ...     print("Index:", item.index)
            ...     print("Value:", item.value)
            ...     print("Type:", item.type)
            ...     print("---")
        """

        try:
            if oids is None:
                oids = []
            if not oids:
                return ()
            return super().get(oids)
        except Exception as e:
            _handle_error(e)

    def get_next(self, oids=None):
        """
        Performs an SNMP GETNEXT operation to retrieve the next object instance for each of the specified OIDs.

        Accepts either a single OID string or a list of OID strings.

        :param oids: A single OID string or a list of Object Identifiers (OIDs) to get
            next values from. Defaults to ``None``, which is treated as an empty list.
        :type oids: Union[str, list[str], None]
        :return: A tuple of Result objects containing SNMP variable bindings with attributes:
            oid (str), index (str), value (str), and type (str)
        :rtype: tuple[Result]

        :raises GenericError: If the exception type is `GenericErrorBase`.
        :raises ConnectionError: If the exception type is `ConnectionErrorBase`.
        :raises NoSuchInstanceError: If the exception type is `NoSuchInstanceErrorBase`.
        :raises NoSuchNameError: If the exception type is `NoSuchNameErrorBase`.
        :raises NoSuchObjectError: If the exception type is `NoSuchObjectErrorBase`.
        :raises PacketError: If the exception type is `PacketErrorBase`.
        :raises ParseError: If the exception type is `ParseErrorBase`.
        :raises TimeoutError: If the exception type is `TimeoutErrorBase`.
        :raises UndeterminedTypeError: If the exception type is `UndeterminedTypeErrorBase`.
        :raises UnknownObjectIDError: If the exception type is `UnknownObjectIDErrorBase`.
        :raises Exception: If the exception type does not match any of the above, the original
            exception `e` is raised.

        Example:
            >>> from ezsnmp import Session
            >>> session = Session(hostname="localhost", community="public", version="2")
            >>> results = session.get_next(["1.3.6.1.2.1.1.1.0"])
            >>> for item in results:
            ...     print("OID:", item.oid)
            ...     print("Index:", item.index)
            ...     print("Value:", item.value)
            ...     print("Type:", item.type)
            ...     print("---")
        """

        try:
            if oids is None:
                oids = []
            if not oids:
                return ()
            return super().get_next(oids)
        except Exception as e:
            _handle_error(e)

    def bulk_get(self, oids=None):
        """
        Performs an SNMP GETBULK operation to retrieve values for one or more OIDs.

        Requires SNMPv2c or SNMPv3. GETBULK is not supported in SNMPv1.

        Accepts either a single OID string or a list of OID strings.

        :param oids: A single OID string or a list of Object Identifiers (OIDs) to retrieve
            values from. Defaults to ``None``, which is treated as an empty list.
        :type oids: Union[str, list[str], None]
        :return: A tuple of Result objects containing SNMP variable bindings with attributes:
            oid (str), index (str), value (str), and type (str)
        :rtype: tuple[Result]

        :raises GenericError: If the exception type is `GenericErrorBase`.
        :raises ConnectionError: If the exception type is `ConnectionErrorBase`.
        :raises NoSuchInstanceError: If the exception type is `NoSuchInstanceErrorBase`.
        :raises NoSuchNameError: If the exception type is `NoSuchNameErrorBase`.
        :raises NoSuchObjectError: If the exception type is `NoSuchObjectErrorBase`.
        :raises PacketError: If the exception type is `PacketErrorBase`.
        :raises ParseError: If the exception type is `ParseErrorBase`.
        :raises TimeoutError: If the exception type is `TimeoutErrorBase`.
        :raises UndeterminedTypeError: If the exception type is `UndeterminedTypeErrorBase`.
        :raises UnknownObjectIDError: If the exception type is `UnknownObjectIDErrorBase`.
        :raises Exception: If the exception type does not match any of the above, the original
            exception `e` is raised.

        Example:
            >>> from ezsnmp import Session
            >>> session = Session(hostname="localhost", community="public", version="2")
            >>> results = session.bulk_get(["1.3.6.1.2.1.1.1.0", "1.3.6.1.2.1.1.2.0"])
            >>> for item in results:
            ...     print("OID:", item.oid)
            ...     print("Index:", item.index)
            ...     print("Value:", item.value)
            ...     print("Type:", item.type)
            ...     print("---")
        """

        try:
            if oids is None:
                oids = []
            self.set_max_repeaters_to_num = self.__set_max_repeaters_to_num
            return self._bulk_get(oids)
        except Exception as e:
            _handle_error(e)
        finally:
            self.set_max_repeaters_to_num = ""

    def _bulk_get(self, oids):
        return super().bulk_get(oids)

    def set(self, oids=None):
        """
        Performs an SNMP SET operation to set values for one or more OIDs.

        :param oids: A flat list of OID/type/value triples. Elements are ordered as
            ``[oid, type, value, oid, type, value, ...]`` where type is a single-character
            string indicating the SNMP data type
            (e.g. ``'i'`` for INTEGER, ``'s'`` for STRING, ``'o'`` for OBJECT IDENTIFIER,
            ``'u'`` for UNSIGNED, ``'t'`` for TIMETICKS, ``'a'`` for IPADDRESS,
            ``'x'`` for HEX STRING). For the full list see
            `snmpset(1) <https://www.net-snmp.org/docs/man/snmpset.html>`_.
            Defaults to ``None``, treated as an empty list.
        :type oids: list
        :return: A tuple of Result objects containing SNMP variable bindings with attributes:
            oid (str), index (str), value (str), and type (str)
        :rtype: tuple[Result]

        :raises GenericError: If the exception type is `GenericErrorBase`.
        :raises ConnectionError: If the exception type is `ConnectionErrorBase`.
        :raises NoSuchInstanceError: If the exception type is `NoSuchInstanceErrorBase`.
        :raises NoSuchNameError: If the exception type is `NoSuchNameErrorBase`.
        :raises NoSuchObjectError: If the exception type is `NoSuchObjectErrorBase`.
        :raises PacketError: If the exception type is `PacketErrorBase`.
        :raises ParseError: If the exception type is `ParseErrorBase`.
        :raises TimeoutError: If the exception type is `TimeoutErrorBase`.
        :raises UndeterminedTypeError: If the exception type is `UndeterminedTypeErrorBase`.
        :raises UnknownObjectIDError: If the exception type is `UnknownObjectIDErrorBase`.
        :raises Exception: If the exception type does not match any of the above, the original
            exception `e` is raised.

        Example:
            >>> from ezsnmp import Session
            >>> session = Session(hostname="localhost", community="public", version="2")
            >>> results = session.set([
            ...     ".1.3.6.1.6.3.12.1.2.1.2.116.101.115.116", "o", ".1.3.6.1.6.1.1",
            ...     ".1.3.6.1.6.3.12.1.2.1.3.116.101.115.116", "s", "1234",
            ...     ".1.3.6.1.6.3.12.1.2.1.9.116.101.115.116", "i", "4"
            ... ])
            >>> for item in results:
            ...     print("OID:", item.oid)
            ...     print("Index:", item.index)
            ...     print("Value:", item.value)
            ...     print("Type:", item.type)
            ...     print("---")
        """

        try:
            if oids is None:
                oids = []
            if not oids:
                return ()
            return self._set(oids)
        except Exception as e:
            _handle_error(e)

    def _set(self, oids):
        return super().set(oids)
