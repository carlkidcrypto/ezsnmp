import warnings
from typing import Any, Dict, Optional

from .sessionbase import SessionBase
from .exceptions import _handle_error, GenericError

_LEGACY_PARAM_SPECS = (
    ("hostname", "connection"),
    ("port_number", "connection"),
    ("version", "connection"),
    ("community", "connection"),
    ("auth_protocol", "v3"),
    ("auth_passphrase", "v3"),
    ("security_engine_id", "v3"),
    ("context_engine_id", "v3"),
    ("security_level", "v3"),
    ("context", "v3"),
    ("security_username", "v3"),
    ("privacy_protocol", "v3"),
    ("privacy_passphrase", "v3"),
    ("boots_time", "v3"),
    ("retries", "connection"),
    ("timeout", "connection"),
    ("load_mibs", "mib"),
    ("mib_directories", "mib"),
    ("print_enums_numerically", "mib"),
    ("print_full_oids", "mib"),
    ("print_oids_numerically", "mib"),
    ("print_timeticks_numerically", "mib"),
    ("print_hex_strings", "mib"),
    ("set_max_repeaters_to_num", "operation"),
)
_LEGACY_PARAM_GROUPS = dict(_LEGACY_PARAM_SPECS)


def _normalize_option_value(key: str, value: Any) -> str:
    """Convert a Python option value into the string representation expected by SessionBase."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if key == "version" and value == 2:
        return "2c"
    return str(value)


def _normalize_option_map(options: Optional[Dict[str, Any]]) -> Dict[str, str]:
    """Normalize an optional dict of session options into ``dict[str, str]``."""
    if not options:
        return {}
    return {str(k): _normalize_option_value(str(k), v) for k, v in options.items()}


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

        with Session(
            connection_options={
                "hostname": "localhost",
                "community": "public",
                "version": 2,
            }
        ) as session:
            results = session.get(["sysDescr.0", "sysLocation.0"])
            for item in results:
                print(item.oid, item.value)
    """

    def __init__(
        self,
        connection_options: Optional[Dict[str, Any]] = None,
        v3_options: Optional[Dict[str, Any]] = None,
        mib_and_output_options: Optional[Dict[str, Any]] = None,
        operation_options: Optional[Dict[str, Any]] = None,
        *legacy_args: Any,
        **legacy_kwargs: Any,
    ):
        """Initialize the Session object with grouped NetSNMP session options.

        :param connection_options: Connection and transport options dictionary.
            Supported keys:

            - ``hostname`` (``str``): Hostname or IP address of the SNMP agent.
            - ``port_number`` (``Union[str, int]``): Port number of the SNMP agent.
            - ``version`` (``Union[str, int]``): SNMP version (``1`` / ``"1"``,
              ``2`` / ``"2"`` / ``"2c"`` where integer ``2`` is converted to
              ``"2c"``, or ``3`` / ``"3"``).
            - ``community`` (``str``): Community string for SNMPv1/v2c.
            - ``retries`` (``Union[str, int]``): Number of retries.
            - ``timeout`` (``Union[str, int]``): Timeout value in seconds.
        :type connection_options: Optional[Dict[str, Any]]
        :param v3_options: SNMPv3 authentication, privacy, and context options
            dictionary. Supported keys:

            - ``auth_protocol`` (``str``): Authentication protocol (e.g., ``"MD5"``, ``"SHA"``).
            - ``auth_passphrase`` (``str``): Authentication passphrase.
            - ``security_engine_id`` (``str``): Security engine ID.
            - ``context_engine_id`` (``str``): Context engine ID.
            - ``security_level`` (``str``): Security level (e.g., ``"noAuthNoPriv"``, ``"authNoPriv"``, ``"authPriv"``).
            - ``context`` (``str``): SNMPv3 context name.
            - ``security_username`` (``str``): Security username.
            - ``privacy_protocol`` (``str``): Privacy protocol (e.g., ``"DES"``, ``"AES"``).
            - ``privacy_passphrase`` (``str``): Privacy passphrase.
            - ``boots_time`` (``str``): Authoritative engine boots and time (``"BOOTS,TIME"``).
        :type v3_options: Optional[Dict[str, Any]]
        :param mib_and_output_options: MIB loading, input parsing, and output
            formatting options dictionary. Supported keys:

            - ``load_mibs`` (``str``): Comma-separated MIB modules to load.
            - ``mib_directories`` (``str``): Comma-separated MIB search directories.
            - ``print_enums_numerically`` (``bool``): Print enums numerically.
            - ``print_full_oids`` (``bool``): Print full OIDs.
            - ``print_oids_numerically`` (``bool``): Print OIDs numerically.
            - ``print_timeticks_numerically`` (``bool``): Print timeticks numerically.
            - ``print_hex_strings`` (``bool``): Print OCTET STRING values in hex.
            - ``print_oid_suffix_only`` (``bool``): Print only the last symbolic OID element (``-O s``).
            - ``print_oid_module_name`` (``bool``): Print module name plus last symbolic element (``-O S``).
            - ``print_oid_ucd_style`` (``bool``): Print OIDs in UCD-style (``-O u``).
            - ``print_ascii_strings`` (``bool``): Print strings as ASCII (``-O a``).
            - ``print_leading_zero_hex`` (``bool``): Print leading zeroes in hex strings (``-O 0``).
            - ``print_hex_text`` (``bool``): Print ASCII text alongside hex output (``-O T``).
            - ``dont_breakdown_oids`` (``bool``): Disable OID index breakdown (``-O b``).
            - ``escape_quotes_in_indexes`` (``bool``): Escape quotes in string indexes (``-O E``).
            - ``extended_index_format`` (``bool``): Print indexes in bracketed extended format (``-O X``).
            - ``dont_print_units`` (``bool``): Suppress MIB units in output (``-O U``).
            - ``output_precision`` (``str``): Precision format string for float/double output (``-O p``).
            - ``regex_oid_matching`` (``bool``): Enable regex OID matching (``-I b``).
            - ``ignore_display_hints`` (``bool``): Ignore MIB DISPLAY-HINTs on input (``-I h``).
            - ``dont_check_range`` (``bool``): Disable range checks on input values (``-I r``).
            - ``random_access_oid`` (``bool``): Enable random-access OID lookup (``-I R``).
            - ``read_ucd_style_oid`` (``bool``): Read OIDs relative to UCD default prefix (``-I u``).
            - ``oid_suffix`` (``str``): Suffix to append to input OIDs (``-I s``).
            - ``oid_prefix`` (``str``): Prefix to prepend to input OIDs (``-I S``).
            - ``mib_allow_underline`` (``bool``): Allow underscores in MIB labels (``-P u``).
            - ``mib_comment_to_eol`` (``bool``): Treat ``--`` MIB comments as extending to EOL (``-P c``).
            - ``mib_replace_with_latest`` (``bool``): Replace duplicate MIB objects with latest definition (``-P R``).
        :type mib_and_output_options: Optional[Dict[str, Any]]
        :param operation_options: SNMP operation behavior options dictionary.
            Supported keys:

            - ``set_max_repeaters_to_num`` (``Union[str, int]``): Max repeaters for GETBULK PDUs (defaults to ``10``; applies to :meth:`bulk_get` and :meth:`bulk_walk`).
            - ``non_repeaters`` (``Union[str, int]``): Non-repeaters for GETBULK PDUs (``-C n``).
            - ``walk_dont_check_lexicographic`` (``bool``): Disable lexicographical OID checks during walks (``-C c``).
            - ``walk_include_requested`` (``bool``): Include requested OID in walk results (``-C i``).
            - ``walk_dont_get_requested`` (``bool``): Skip GET fallback when walk returns nothing (``-C I``).
            - ``walk_end_oid`` (``str``): OID at which to stop walking (``-C E``).
            - ``dont_fix_pdus`` (``bool``): Disable PDU error fixing on GET/GETNEXT (``-C f``).
        :type operation_options: Optional[Dict[str, Any]]
        :param legacy_args: Deprecated legacy flat positional arguments.
        :param legacy_kwargs: Deprecated legacy flat keyword arguments.

        .. deprecated::
            Passing individual flat positional or keyword parameters to
            ``Session.__init__()`` is deprecated and will be removed in a
            future release. Pass grouped dictionaries (``connection_options``,
            ``v3_options``, ``mib_and_output_options``, ``operation_options``)
            instead.
        """

        first_four = (
            connection_options,
            v3_options,
            mib_and_output_options,
            operation_options,
        )
        is_legacy_positional = bool(legacy_args) or any(
            arg is not None and not isinstance(arg, dict) for arg in first_four
        )

        if is_legacy_positional:
            if legacy_args:
                positional_legacy = first_four + legacy_args
            else:
                end = len(first_four)
                while end > 0 and first_four[end - 1] is None:
                    end -= 1
                positional_legacy = first_four[:end]

            if len(positional_legacy) > len(_LEGACY_PARAM_SPECS):
                raise TypeError(
                    f"Session.__init__() takes at most {len(_LEGACY_PARAM_SPECS)} positional "
                    f"arguments ({len(positional_legacy)} given)"
                )

            conn_opts: Dict[str, str] = {}
            v3_opts: Dict[str, str] = {}
            mib_opts: Dict[str, str] = {}
            op_opts: Dict[str, str] = {}
        else:
            positional_legacy = ()
            conn_opts = _normalize_option_map(connection_options)
            v3_opts = _normalize_option_map(v3_options)
            mib_opts = _normalize_option_map(mib_and_output_options)
            op_opts = _normalize_option_map(operation_options)

        group_targets = {
            "connection": conn_opts,
            "v3": v3_opts,
            "mib": mib_opts,
            "operation": op_opts,
        }

        used_legacy_params = False
        seen_legacy_names = set()

        for (param_name, group_name), val in zip(
            _LEGACY_PARAM_SPECS, positional_legacy
        ):
            used_legacy_params = True
            seen_legacy_names.add(param_name)
            group_targets[group_name][param_name] = _normalize_option_value(
                param_name, val
            )

        for key, val in legacy_kwargs.items():
            group_name = _LEGACY_PARAM_GROUPS.get(key)
            if group_name is None:
                raise TypeError(
                    f"Session.__init__() got an unexpected keyword argument '{key}'"
                )
            if key in seen_legacy_names:
                raise TypeError(
                    f"Session.__init__() got multiple values for argument '{key}'"
                )
            used_legacy_params = True
            seen_legacy_names.add(key)
            group_targets[group_name][key] = _normalize_option_value(key, val)

        if used_legacy_params:
            warnings.warn(
                "Passing individual flat parameters to Session.__init__() is deprecated and "
                "will be removed in a future release. Pass grouped dictionaries "
                "(connection_options, v3_options, mib_and_output_options, operation_options) "
                "instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        # Note that underlying SessionBase object depends on all parameters to be strings.
        # This is the case, since at the end of the day we are building a command line string
        # to pass to the NetSNMP command line tool.
        try:
            max_repeaters = op_opts.pop("set_max_repeaters_to_num", "10")

            # Initialize the SWIG-wrapped C++ SessionBase via super().__init__().
            # This ensures that calling inherited methods like _get_context() directly
            # on the Session object works correctly (fixes GitHub issue #656).
            super().__init__(conn_opts, v3_opts, mib_opts, op_opts)

            # Track the closed state for __del__ and multiple closes
            self._closed = False
            self.__set_max_repeaters_to_num = max_repeaters

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
