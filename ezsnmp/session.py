from .sessionbase import SessionBase


class Session(SessionBase):
    """
    Python wrapper class for SessionBase, providing a Pythonic interface
    for managing NetSNMP sessions.
    """

    def __init__(
        self,
        hostname="localhost",
        port_number="",
        version="3",
        community="public",
        auth_protocol="",
        auth_passphrase="",
        security_engine_id="",
        context_engine_id="",
        security_level="",
        context="",
        security_username="",
        privacy_protocol="",
        privacy_passphrase="",
        boots_time="",
        retries="3",
        timeout="1",
    ):
        """
        Initialize the Session object with NetSNMP session parameters.
        """
        super().__init__(
            hostname,
            port_number,
            version,
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
            retries,
            timeout,
        )

    @property
    def args(self):
        """Get the list of arguments used for NetSNMP commands."""
        return self._get_args()

    @property
    def hostname(self):
        """Get the hostname or IP address of the SNMP agent."""
        return self._get_hostname()

    @hostname.setter
    def hostname(self, value):
        """Set the hostname or IP address of the SNMP agent."""
        self._set_hostname(value)

    @property
    def port_number(self):
        """Get the port number of the SNMP agent."""
        return self._get_port_number()

    @port_number.setter
    def port_number(self, value):
        """Set the port number of the SNMP agent."""
        self._set_port_number(value)

    @property
    def version(self):
        """Get the SNMP version being used."""
        return self._get_version()

    @version.setter
    def version(self, value):
        """Set the SNMP version to use."""
        self._set_version(value)

    @property
    def community(self):
        """Get the community string for SNMPv1/v2c."""
        return self._get_community()

    @community.setter
    def community(self, value):
        """Set the community string for SNMPv1/v2c."""
        self._set_community(value)

    @property
    def auth_protocol(self):
        """Get the authentication protocol."""
        return self._get_auth_protocol()

    @auth_protocol.setter
    def auth_protocol(self, value):
        """Set the authentication protocol."""
        self._set_auth_protocol(value)

    @property
    def auth_passphrase(self):
        """Get the authentication passphrase."""
        return self._get_auth_passphrase()

    @auth_passphrase.setter
    def auth_passphrase(self, value):
        """Set the authentication passphrase."""
        self._set_auth_passphrase(value)

    @property
    def security_engine_id(self):
        """Get the security engine ID."""
        return self._get_security_engine_id()

    @security_engine_id.setter
    def security_engine_id(self, value):
        """Set the security engine ID."""
        self._set_security_engine_id(value)

    @property
    def context_engine_id(self):
        """Get the context engine ID."""
        return self._get_context_engine_id()

    @context_engine_id.setter
    def context_engine_id(self, value):
        """Set the context engine ID."""
        self._set_context_engine_id(value)

    @property
    def security_level(self):
        """Get the security level."""
        return self._get_security_level()

    @security_level.setter
    def security_level(self, value):
        """Set the security level."""
        self._set_security_level(value)

    @property
    def context(self):
        """Get the context."""
        return self._get_context()

    @context.setter
    def context(self, value):
        """Set the context."""
        self._set_context(value)

    @property
    def security_username(self):
        """Get the security username."""
        return self._get_security_username()

    @security_username.setter
    def security_username(self, value):
        """Set the security username."""
        self._set_security_username(value)

    @property
    def privacy_protocol(self):
        """Get the privacy protocol."""
        return self._get_privacy_protocol()

    @privacy_protocol.setter
    def privacy_protocol(self, value):
        """Set the privacy protocol."""
        self._set_privacy_protocol(value)

    @property
    def privacy_passphrase(self):
        """Get the privacy passphrase."""
        return self._get_privacy_passphrase()

    @privacy_passphrase.setter
    def privacy_passphrase(self, value):
        """Set the privacy passphrase."""
        self._set_privacy_passphrase(value)

    @property
    def boots_time(self):
        """Get the boots time."""
        return self._get_boots_time()

    @boots_time.setter
    def boots_time(self, value):
        """Set the boots time."""
        self._set_boots_time(value)

    @property
    def retries(self):
        """Get the number of retries."""
        return self._get_retries()

    @retries.setter
    def retries(self, value):
        """Set the number of retries."""
        self._set_retries(value)

    @property
    def timeout(self):
        """Get the timeout value."""
        return self._get_timeout()

    @timeout.setter
    def timeout(self, value):
        """Set the timeout value."""
        self._set_timeout(value)
