import unittest
import faulthandler
from ezsnmp import Session
from unittest_fixtures import BaseTestCase

faulthandler.enable()


class TestPropertyGetters(BaseTestCase):
    def test_context_engine_id_getter(self):
        """
        Given a Session configured with SNMPv3 MD5/DES authentication
        When accessing the context_engine_id property
        Then it should return a string or None without raising an error
        """
        sess = Session(**self.sess_v3_md5_des)
        engine_id = sess.context_engine_id
        self.assertTrue(isinstance(engine_id, str) or engine_id is None)

    def test_context_getter(self):
        """
        Given a Session configured with SNMPv3 MD5/DES authentication
        When accessing the context property
        Then it should return a string or None without raising an error
        """
        sess = Session(**self.sess_v3_md5_des)
        context = sess.context
        self.assertTrue(isinstance(context, str) or context is None)

    def test_boots_time_getter(self):
        """
        Given a Session configured with SNMPv3 MD5/DES authentication
        When accessing the boots_time property
        Then it should return a non-None value
        """
        sess = Session(**self.sess_v3_md5_des)
        boots_time = sess.boots_time
        self.assertIsNotNone(boots_time)

    def test_security_engine_id_getter(self):
        """
        Given a Session configured with SNMPv3 MD5/DES authentication
        When accessing the security_engine_id property
        Then it should return a string or None without raising an error
        """
        sess = Session(**self.sess_v3_md5_des)
        engine_id = sess.security_engine_id
        self.assertTrue(isinstance(engine_id, str) or engine_id is None)


if __name__ == '__main__':
    unittest.main()
