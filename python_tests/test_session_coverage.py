"""
Tests to achieve 100% coverage for Session class edge cases and missing paths.
"""
import pytest
import faulthandler
from ezsnmp import Session

faulthandler.enable()


def test_session_context_manager():
    """Test Session as context manager with __enter__ and __exit__."""
    with Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    ) as sess:
        # Verify we got the session object back
        assert isinstance(sess, Session)
        assert sess.hostname == "localhost"
        assert sess.port_number == "11161"
    
    # After exiting context, session should be closed via __exit__
    # The session is closed but we can't easily test that without accessing internals


def test_session_destructor_cleanup():
    """Test that __del__ properly cleans up the session."""
    sess = Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    )
    
    # Verify session was created
    assert sess.hostname == "localhost"
    
    # Delete the session object to trigger __del__
    del sess
    
    # If we get here without errors, __del__ worked


def test_session_hostname_setter():
    """Test setting hostname property."""
    sess = Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    )
    
    # Set a new hostname
    sess.hostname = "127.0.0.1"
    assert sess.hostname == "127.0.0.1"


def test_session_port_number_setter():
    """Test setting port_number property."""
    sess = Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    )
    
    # Set a new port number
    sess.port_number = "11162"
    assert sess.port_number == "11162"


def test_session_version_setter():
    """Test setting version property."""
    sess = Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    )
    
    # Set a new version
    sess.version = "1"
    assert sess.version == "1"


def test_session_community_setter():
    """Test setting community property."""
    sess = Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    )
    
    # Set a new community
    sess.community = "private"
    assert sess.community == "private"


def test_session_retries_setter():
    """Test setting retries property."""
    sess = Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    )
    
    # Set new retries value
    sess.retries = "5"
    assert sess.retries == "5"


def test_session_timeout_setter():
    """Test setting timeout property."""
    sess = Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    )
    
    # Set new timeout value
    sess.timeout = "10"
    assert sess.timeout == "10"


def test_session_security_username_setter(sess_v3_md5_des):
    """Test setting security_username property."""
    sess = Session(**sess_v3_md5_des)
    
    # Set new security username
    sess.security_username = "new_user"
    assert sess.security_username == "new_user"


def test_session_security_level_setter(sess_v3_md5_des):
    """Test setting security_level property."""
    sess = Session(**sess_v3_md5_des)
    
    # Set new security level
    sess.security_level = "authNoPriv"
    assert sess.security_level == "authNoPriv"


def test_session_auth_protocol_setter(sess_v3_md5_des):
    """Test setting auth_protocol property."""
    sess = Session(**sess_v3_md5_des)
    
    # Set new auth protocol
    sess.auth_protocol = "SHA"
    assert sess.auth_protocol == "SHA"


def test_session_auth_passphrase_setter(sess_v3_md5_des):
    """Test setting auth_passphrase property."""
    sess = Session(**sess_v3_md5_des)
    
    # Set new auth passphrase
    sess.auth_passphrase = "new_auth_pass"
    assert sess.auth_passphrase == "new_auth_pass"


def test_session_privacy_protocol_setter(sess_v3_md5_des):
    """Test setting privacy_protocol property."""
    sess = Session(**sess_v3_md5_des)
    
    # Set new privacy protocol
    sess.privacy_protocol = "AES"
    assert sess.privacy_protocol == "AES"


def test_session_privacy_passphrase_setter(sess_v3_md5_des):
    """Test setting privacy_passphrase property."""
    sess = Session(**sess_v3_md5_des)
    
    # Set new privacy passphrase
    sess.privacy_passphrase = "new_priv_pass"
    assert sess.privacy_passphrase == "new_priv_pass"


def test_session_context_engine_id_setter(sess_v3_md5_des):
    """Test setting context_engine_id property."""
    sess = Session(**sess_v3_md5_des)
    
    # Set new context engine ID
    sess.context_engine_id = "80001F8880E9630000D61FF449"
    assert sess.context_engine_id == "80001F8880E9630000D61FF449"


def test_session_context_setter(sess_v3_md5_des):
    """Test setting context property."""
    sess = Session(**sess_v3_md5_des)
    
    # Set new context
    sess.context = "new_context"
    assert sess.context == "new_context"


def test_session_use_sprint_value_setter():
    """Test setting use_sprint_value property."""
    sess = Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    )
    
    # Set use_sprint_value
    sess.use_sprint_value = True
    assert sess.use_sprint_value is True
    
    sess.use_sprint_value = False
    assert sess.use_sprint_value is False


def test_session_use_enums_setter():
    """Test setting use_enums property."""
    sess = Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    )
    
    # Set use_enums
    sess.use_enums = True
    assert sess.use_enums is True
    
    sess.use_enums = False
    assert sess.use_enums is False


def test_session_use_long_names_setter():
    """Test setting use_long_names property."""
    sess = Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    )
    
    # Set use_long_names
    sess.use_long_names = True
    assert sess.use_long_names is True
    
    sess.use_long_names = False
    assert sess.use_long_names is False


def test_session_use_numeric_setter():
    """Test setting use_numeric property."""
    sess = Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    )
    
    # Set use_numeric
    sess.use_numeric = True
    assert sess.use_numeric is True
    
    sess.use_numeric = False
    assert sess.use_numeric is False


def test_session_best_guess_setter():
    """Test setting best_guess property."""
    sess = Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    )
    
    # Set best_guess
    sess.best_guess = 1
    assert sess.best_guess == 1
    
    sess.best_guess = 0
    assert sess.best_guess == 0


def test_session_non_increasing_setter():
    """Test setting non_increasing property."""
    sess = Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    )
    
    # Set non_increasing
    sess.non_increasing = True
    assert sess.non_increasing is True
    
    sess.non_increasing = False
    assert sess.non_increasing is False


def test_session_use_snmpget_bulk_setter():
    """Test setting use_snmpget_bulk property."""
    sess = Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    )
    
    # Set use_snmpget_bulk
    sess.use_snmpget_bulk = True
    assert sess.use_snmpget_bulk is True
    
    sess.use_snmpget_bulk = False
    assert sess.use_snmpget_bulk is False


def test_session_use_snmpwalk_bulk_setter():
    """Test setting use_snmpwalk_bulk property."""
    sess = Session(
        hostname="localhost",
        port_number="11161",
        version="2",
        community="public"
    )
    
    # Set use_snmpwalk_bulk
    sess.use_snmpwalk_bulk = True
    assert sess.use_snmpwalk_bulk is True
    
    sess.use_snmpwalk_bulk = False
    assert sess.use_snmpwalk_bulk is False
