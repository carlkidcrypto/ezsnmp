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

    @property
    def port_number(self):
        """Get the port number of the SNMP agent."""
        return self._get_port_number()

    @property
    def version(self):
        """Get the SNMP version being used."""
        return self._get_version()

    @property
    def community(self):
        """Get the community string for SNMPv1/v2c."""
        return self._get_community()

    @property
    def auth_protocol(self):
        """Get the authentication protocol."""
        return self._get_auth_protocol()

    @property
    def auth_passphrase(self):
        """Get the authentication passphrase."""
        return self._get_auth_passphrase()

    @property
    def security_engine_id(self):
        """Get the security engine ID."""
        return self._get_security_engine_id()

    @property
    def context_engine_id(self):
        """Get the context engine ID."""
        return self._get_context_engine_id()

    @property
    def security_level(self):
        """Get the security level."""
        return self._get_security_level()

    @property
    def context(self):
        """Get the context."""
        return self._get_context()

    @property
    def security_username(self):
        """Get the security username."""
        return self._get_security_username()

    @property
    def privacy_protocol(self):
        """Get the privacy protocol."""
        return self._get_privacy_protocol()

    @property
    def privacy_passphrase(self):
        """Get the privacy passphrase."""
        return self._get_privacy_passphrase()

    @property
    def boots_time(self):
        """Get the boots time."""
        return self._get_boots_time()

    @property
    def retries(self):
        """Get the number of retries."""
        return self._get_retries()

    @property
    def timeout(self):
        """Get the timeout value."""
        return self._get_timeout()
