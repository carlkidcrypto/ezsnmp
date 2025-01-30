from .sessionbase import SessionBase
from .exceptions import _handle_error


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
        """Initialize the SessionBase object with NetSNMP session parameters.

        :param hostname: The hostname or IP address of the SNMP agent.
        :type hostname: str
        :param port_number: The port number of the SNMP agent.
        :type port_number: str
        :param version: The SNMP version to use (1, 2c, or 3).
        :type version: str
        :param community: The community string for SNMPv1/v2c.
        :type community: str
        :param auth_protocol: The authentication protocol (e.g., 'MD5', 'SHA').
        :type auth_protocol: str
        :param auth_passphrase: The authentication passphrase.
        :type auth_passphrase: str
        :param security_engine_id: The security engine ID.
        :type security_engine_id: str
        :param context_engine_id: The context engine ID.
        :type context_engine_id: str
        :param security_level: The security level (e.g., 'noAuthNoPriv', 'authNoPriv', 'authPriv').
        :type security_level: str
        :param context: The context.
        :type context: str
        :param security_username: The security username.
        :type security_username: str
        :param privacy_protocol: The privacy protocol (e.g., 'DES', 'AES').
        :type privacy_protocol: str
        :param privacy_passphrase: The privacy passphrase.
        :type privacy_passphrase: str
        :param boots_time: The boots time.
        :type boots_time: str
        :param retries: The number of retries.
        :type retries: str
        :param timeout: The timeout value in seconds.
        :type timeout: str
        """

        try:
            self._session_base = SessionBase(
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

        except Exception as e:
            _handle_error(e)

    @property
    def args(self):
        """Get the list of arguments used for NetSNMP commands.

        :type: list
        """
        result = self._session_base._get_args()
        return result

    @property
    def hostname(self):
        """Get the hostname or IP address of the SNMP agent.

        :type: str
        """
        result = self._session_base._get_hostname()
        return result

    @hostname.setter
    def hostname(self, value):
        """Set the hostname or IP address of the SNMP agent.

        :param value: The hostname or IP address to set.
        :type value: str
        """
        self._session_base._set_hostname(value)

    @property
    def port_number(self):
        """Get the port number of the SNMP agent.

        :type: str
        """
        result = self._session_base._get_port_number()
        return result

    @port_number.setter
    def port_number(self, value):
        """Set the port number of the SNMP agent.

        :param value: The port number to set.
        :type value: str
        """
        self._session_base._set_port_number(value)

    @property
    def version(self):
        """Get the SNMP version being used.

        :type: str
        """
        result = self._session_base._get_version()
        return result

    @version.setter
    def version(self, value):
        """Set the SNMP version to use.

        :param value: The SNMP version to set (1, 2c, or 3).
        :type value: str
        """
        self._session_base._set_version(value)

    @property
    def community(self):
        """Get the community string for SNMPv1/v2c.

        :type: str
        """
        result = self._session_base._get_community()
        return result

    @community.setter
    def community(self, value):
        """Set the community string for SNMPv1/v2c.

        :param value: The community string to set.
        :type value: str
        """
        self._session_base._set_community(value)

    @property
    def auth_protocol(self):
        """Get the authentication protocol.

        :type: str
        """
        result = self._session_base._get_auth_protocol()
        return result

    @auth_protocol.setter
    def auth_protocol(self, value):
        """Set the authentication protocol.

        :param value: The authentication protocol to set (e.g., 'MD5', 'SHA').
        :type value: str
        """
        self._session_base._set_auth_protocol(value)

    @property
    def auth_passphrase(self):
        """Get the authentication passphrase.

        :type: str
        """
        result = self._session_base._get_auth_passphrase()
        return result

    @auth_passphrase.setter
    def auth_passphrase(self, value):
        """Set the authentication passphrase.

        :param value: The authentication passphrase to set.
        :type value: str
        """
        self._session_base._set_auth_passphrase(value)

    @property
    def security_engine_id(self):
        """Get the security engine ID.

        :type: str
        """
        result = self._session_base._get_security_engine_id()
        return result

    @security_engine_id.setter
    def security_engine_id(self, value):
        """Set the security engine ID.

        :param value: The security engine ID to set.
        :type value: str
        """
        self._session_base._set_security_engine_id(value)

    @property
    def context_engine_id(self):
        """Get the context engine ID.

        :type: str
        """
        result = self._session_base._get_context_engine_id()
        return result

    @context_engine_id.setter
    def context_engine_id(self, value):
        """Set the context engine ID.

        :param value: The context engine ID to set.
        :type value: str
        """
        self._session_base._set_context_engine_id(value)

    @property
    def security_level(self):
        """Get the security level.

        :type: str
        """
        result = self._session_base._get_security_level()
        return result

    @security_level.setter
    def security_level(self, value):
        """Set the security level.

        :param value: The security level to set (e.g., 'noAuthNoPriv', 'authNoPriv', 'authPriv').
        :type value: str
        """
        self._session_base._set_security_level(value)

    @property
    def context(self):
        """Get the context.

        :type: str
        """
        result = self._session_base._get_context()
        return result

    @context.setter
    def context(self, value):
        """Set the context.

        :param value: The context to set.
        :type value: str
        """
        self._session_base._set_context(value)

    @property
    def security_username(self):
        """Get the security username.

        :type: str
        """
        result = self._session_base._get_security_username()
        return result

    @security_username.setter
    def security_username(self, value):
        """Set the security username.

        :param value: The security username to set.
        :type value: str
        """
        self._session_base._set_security_username(value)

    @property
    def privacy_protocol(self):
        """Get the privacy protocol.

        :type: str
        """
        result = self._session_base._get_privacy_protocol()
        return result

    @privacy_protocol.setter
    def privacy_protocol(self, value):
        """Set the privacy protocol.

        :param value: The privacy protocol to set (e.g., 'DES', 'AES').
        :type value: str
        """
        self._session_base._set_privacy_protocol(value)

    @property
    def privacy_passphrase(self):
        """Get the privacy passphrase.

        :type: str
        """
        result = self._session_base._get_privacy_passphrase()
        return result

    @privacy_passphrase.setter
    def privacy_passphrase(self, value):
        """Set the privacy passphrase.

        :param value: The privacy passphrase to set.
        :type value: str
        """
        self._session_base._set_privacy_passphrase(value)

    @property
    def boots_time(self):
        """Get the boots time.

        :type: str
        """
        result = self._session_base._get_boots_time()
        return result

    @boots_time.setter
    def boots_time(self, value):
        """Set the boots time.

        :param value: The boots time to set.
        :type value: str
        """
        self._session_base._set_boots_time(value)

    @property
    def retries(self):
        """Get the number of retries.

        :type: int
        """
        result = self._session_base._get_retries()
        return result

    @retries.setter
    def retries(self, value):
        """Set the number of retries.

        :param value: The number of retries to set.
        :type value: int
        """
        self._session_base._set_retries(value)

    @property
    def timeout(self):
        """Get the timeout value.

        :type: int
        """
        result = self._session_base._get_timeout()
        return result

    @timeout.setter
    def timeout(self, value):
        """Set the timeout value.

        :param value: The timeout value to set in seconds.
        :type value: int
        """
        self._session_base._set_timeout(value)

    def walk(self, oid=""):
        try:
            result = self._session_base.walk(oid)
            return result
        except Exception as e:
            _handle_error(e)

    def bulk_walk(self, oid=""):
        try:
            result = self._session_base.bulk_walk(oid)
            return result
        except Exception as e:
            _handle_error(e)

    def bulk_walk(self, oids=[]):
        try:
            result = self._session_base.bulk_walk(oids)
            return result
        except Exception as e:
            _handle_error(e)

    def get(self, oid=""):
        try:
            result = self._session_base.get(oid)
            return result
        except Exception as e:
            _handle_error(e)

    def get(self, oids=[]):
        try:
            result = self._session_base.get(oids)
            return result
        except Exception as e:
            _handle_error(e)

    def get_next(self, oids=[]):
        try:
            result = self._session_base.get_next(oids)
            return result
        except Exception as e:
            _handle_error(e)

    def bulk_get(self, oids=[]):
        try:
            result = self._session_base.bulk_get(oids)
            return result
        except Exception as e:
            _handle_error(e)

    def set(self, oids=[]):
        try:
            result = self._session_base.set(oids)
            return result
        except Exception as e:
            _handle_error(e)
