.. Ez SNMP documentation master file, created by
   sphinx-quickstart on Thu Dec 28 15:32:26 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Ez SNMP's documentation!
===================================

Installation
------------
EzSNMP has been tested and is supported on systems running Net-SNMP
5.9.x and newer. All non-EOL versions of Python 3 are fully supported.

If your OS ships with a supported version of Net-SNMP, then you can install it
without compiling it via your package manager:

On RHEL / CentOS systems:

.. code-block:: bash

    sudo yum install net-snmp-devel

On Debian / Ubuntu systems:

.. code-block:: bash
    
    sudo apt update && sudo apt upgrade -y;
    sudo apt install -y libsnmp-dev libperl-dev snmp-mibs-downloader;

On macOS systems:

.. code-block:: bash

    brew install net-snmp

If your OS doesn't ship with Net-SNMP 5.9.x or newer, please follow instructions
provided on the `Net-SNMP install page <http://www.net-snmp.org/docs/INSTALL.html>`_
to build and install Net-SNMP on your system.

You'll also need to ensure that you have the following packages installed so
that EzSNMP installs correctly:

On RHEL / CentOS systems:

.. code-block:: bash

    sudo yum install gcc python3-devel

On Debian / Ubuntu systems:

.. code-block:: bash

    sudo apt-get install gcc python3-dev

On macOS systems:

.. code-block:: bash

    brew install gcc

Install EzSNMP via pip as follows:

.. code-block:: bash

    pip install ezsnmp

Note: We use `cibuildwheel <https://pypi.org/project/cibuildwheel/>` to make EzSNMP compatiabile
with as many as possible linux distros. Occasionally it isn't perfect. If you have issues try
something like this:

.. code-block:: bash

    pip install --force-reinstall --no-binary :all: ezsnmp


Quick Start
-----------
There are primarily two ways you can use the EzSNMP library.

The first is with the use of a Session object which is most suitable when you
are planning on requesting multiple pieces of SNMP data from a source.

.. code-block:: python

    from ezsnmp import Session

    # Create an SNMP session to be used for all our requests
    session = Session(hostname='localhost', community='public', version=2)

    # You may retrieve an individual OID using an SNMP GET
    location = session.get('sysLocation.0')

    # You may also specify the OID as a tuple (name, index)
    # Note: the index is specified as a string as it can be of other types than
    # just a regular integer
    contact = session.get(('sysContact', '0'))

    # And of course, you may use the numeric OID too
    description = session.get('.1.3.6.1.2.1.1.1.0')

    # Set a variable using an SNMP SET
    session.set('sysLocation.0', 'The SNMP Lab')

    # Perform an SNMP walk
    system_items = session.walk('system')

    # Each returned item can be used normally as its related type (str or int)
    # but also has several extended attributes with SNMP-specific information
    for item in system_items:
        print '{oid}.{oid_index} {snmp_type} = {value}'.format(
            oid=item.oid,
            oid_index=item.oid_index,
            snmp_type=item.snmp_type,
            value=item.value
        )

You may also use EzSNMP via its simple interface which is intended for
one-off operations where you wish to specify all details in the request:

.. code-block:: python

    from ezsnmp import snmp_get, snmp_set, snmp_walk

    # Grab a single piece of information using an SNMP GET
    snmp_get('sysDescr.0', hostname='localhost', community='public', version=1)

    # Perform an SNMP SET to update data
    snmp_set(
        'sysLocation.0', 'My Cool Place',
        hostname='localhost', community='public', version=1
    )

    # Perform an SNMP walk
    snmp_walk('system', hostname='localhost', community='public', version=1)

Example Session Kargs
---------------------

.. code-block:: python

    from ezsnmp.session import Session

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

    # Use the kargs you want. For example
    s = Session(**SESS_V3_MD5_NO_PRIV_ARGS)
    res = s.get("sysDescr.0")

    # Do stuff with res
    print(res)

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
