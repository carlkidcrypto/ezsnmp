=======
Ez SNMP
=======

|Python Code Style| |Black| |Pull Request Sphinx Docs Check| |PyPI Distributions| |TestPyPI Distributions| |Tests| |License|

.. |Python Code Style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
.. |Black| image:: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/black.yml/badge.svg
    :target: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/black.yml
.. |Pull Request Sphinx Docs Check| image:: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/sphinx_build.yml/badge.svg
    :target: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/sphinx_build.yml
.. |PyPI Distributions| image:: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/build_and_publish_to_pypi.yml/badge.svg
    :target: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/build_and_publish_to_pypi.yml
.. |TestPyPI Distributions| image:: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/build_and_publish_to_test_pypi.yml/badge.svg
    :target: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/build_and_publish_to_test_pypi.yml
.. |Tests| image:: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/tests.yml
.. |License| image:: https://img.shields.io/badge/license-BSD-blue.svg
    :target: https://github.com/carlkidcrypto/ezsnmp/blob/master/LICENSE

.. image:: https://github.com/carlkidcrypto/ezsnmp/blob/main/images/ezsnmp-logo.png
    :alt: Ez SNMP Logo

Artwork courtesy of `Open Clip Art
Library <https://openclipart.org/detail/251135/simple-network>`__


Introduction
------------

Ez SNMP is a fork of `Easy SNMP <http://net-snmp.sourceforge.net/wiki/index.php/Python_Bindings>`__

Why Another Library?
--------------------

- Simple, because the maintainer of `Easy SNMP` seems to have abandoned the project and or isn't actively working on it.
- This version (Ez SNMP) will attempt to remain up to date with Python versions that are supported by `Python <https://devguide.python.org/versions/>`__
  and net-snmp versions that are supported by `Net-SNMP <http://www.net-snmp.org/download.html>`__

Quick Start
-----------

There are primarily two ways you can use the Ez SNMP library:

1. By using a Session object which is most suitable
when you want to request multiple pieces of SNMP data from a
source:

.. code:: python

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

2. By using Ez SNMP via its simple interface which is intended
for one-off operations (where you wish to specify all details in the
request):

.. code:: python

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

Documentation
-------------

Please check out the `Ez SNMP documentation at <http://carlkidcrypto.github.io/ezsnmp/>`_. This includes installation
instructions for various operating systems.

You may generate the documentation as follows:

.. code:: bash

    # Install Sphinx
    # See this website for install instructions https://www.sphinx-doc.org/en/master/usage/installation.html

    # Build the documentation into static HTML pages
    cd sphinx_docs_build
    make html

Acknowledgments
---------------

I'd like to say thanks to the following folks who have made this project
possible:

-  **Giovanni Marzot**: the original author
-  **ScienceLogic, LLC**: sponsored the initial development of this
   module
-  **Wes Hardaker and the net-snmp-coders**: for their hard work and
   dedication
- **fgimian and nnathan**: the original contributors to this codebase
- **Kent Coble**: who as the most recent maintainer. `Easy SNMP <https://github.com/easysnmp/easysnmp>`_

Running Tests
-------------

Tests use `Pytest <https://github.com/pytest-dev/pytest>`_. You can run
them with the following on Linux:

.. code:: bash

    git clone https://github.com/ezsnmp/ezsnmp.git;
    cd ezsnmp;
    mv /etc/snmp/snmpd.conf /etc/snmp/snmpd.conf.orig;
    cp tests/snmpd.conf /etc/snmp/snmpd.conf;
    systemctl start snmpd;
    rm -drf build/ ezsnmp.egg-info;
    python3 setup.py build && python3 -m pip install -e . && gdb -ex run -ex bt -ex quit --args python3 -m pytest .;


On MacOS

.. code:: bash

    git clone https://github.com/ezsnmp/ezsnmp.git;
    cd ezsnmp;
    mv /etc/snmp/snmpd.conf /etc/snmp/snmpd.conf.orig;
    cp tests/snmpd.conf /etc/snmp/snmpd.conf;
    launchctl unload /System/Library/LaunchDaemons/org.net-snmp.snmpd.plist;
    launchctl load -w /System/Library/LaunchDaemons/org.net-snmp.snmpd.plist;
    rm -drf build/ ezsnmp.egg-info;
    python3 setup.py build && python3 -m pip install -e . && python3 -m pytest .;

License
-------

Ez SNMP is released under the **BSD** license. Please see the
`LICENSE <https://github.com/ezsnmp/ezsnmp/blob/master/LICENSE>`_
file for more details.

Copyright
---------

The original version of this library is copyright (c) 2006 G. S. Marzot.
All rights reserved.

This program is free software; you can redistribute it and/or modify it
under the same terms as Net-SNMP itself.

Copyright (c) 2006 SPARTA, Inc. All Rights Reserved. This program is
free software; you can redistribute it and/or modify it under the same
terms as Net-SNMP itself.

Copyright (c) 2023 carlkidcrypto All Rights Reserved. This program is
free software; you can redistribute it and/or modify it under the same
terms as Net-SNMP itself.
