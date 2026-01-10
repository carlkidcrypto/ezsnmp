Migration Guide: V1.X.X to V2.X.X
=================================

This guide outlines the changes required to migrate from V1.X.X to V2.X.X.

Major Changes
-------------

- The ``Session`` class has been refactored to use string parameters instead of mixed types
- Many parameters have been removed or renamed for clarity
- Default values have been modified for several parameters

Parameter Changes
-----------------

Renamed Parameters
~~~~~~~~~~~~~~~~~~

- ``remote_port`` → ``port_number``
- ``privacy_password`` → ``privacy_passphrase``
- ``auth_password`` → ``auth_passphrase``
- ``use_numeric`` → ``print_oids_numerically``
- ``use_long_names`` → ``print_full_oids``
- ``use_enums`` → ``print_enums_numerically``

Removed Parameters
~~~~~~~~~~~~~~~~~~

The following parameters have been removed in V2.X.X and will be reintroduced in future releases, 
as we focus on stabilizing core functionality:

- ``local_port``
- ``engine_boots`` 
- ``engine_time``
- ``our_identity``
- ``their_identity``
- ``their_hostname``
- ``trust_cert``
- ``use_sprint_value``
- ``best_guess``
- ``retry_no_such``
- ``abort_on_nonexistent``

Parameter Value Changes
-----------------------

In V2.X.X, all parameters have updated acceptable values to align with the requirements of the
underlying net-snmp applications. For example:

``security_level``: In V1.X.X, this parameter accepted values like ``auth_with_privacy``. In
V2.X.X, the possible values are now ``noAuthNoPriv``, ``authNoPriv``, and ``authPriv``, as
required by net-snmp tools like ``snmpwalk``.

For more details on the acceptable values for ``security_level`` and other parameters, refer to the 
official net-snmp documentation: `Net-SNMP Command Line Applications 
<http://www.net-snmp.org/docs/man/snmpcmd.html>`_.

Parameter Mapping Table
-----------------------

The following table maps EzSnmp parameter names to their corresponding net-snmp parameter options:

.. list-table:: EzSnmp to Net-SNMP Parameter Mapping
     :header-rows: 1

     * - EzSnmp Parameter
       - Net-SNMP Parameter Option
     * - ``version``
       - ``-v VERSION``
     * - ``community``
       - ``-c COMMUNITY``
     * - ``security_level``
       - ``-l LEVEL``
     * - ``auth_protocol``
       - ``-a PROTOCOL``
     * - ``auth_passphrase``
       - ``-A PASSPHRASE``
     * - ``privacy_protocol``
       - ``-x PROTOCOL``
     * - ``privacy_passphrase``
       - ``-X PASSPHRASE``
     * - ``security_username``
       - ``-u USERNAME``
     * - ``context_name``
       - ``-n CONTEXT``
     * - ``security_engine_id``
       - ``-e ENGINE-ID``
     * - ``context_engine_id``
       - ``-E ENGINE-ID``
     * - ``boots_time``
       - ``-Z BOOTS,TIME``
     * - ``timeout``
       - ``-t TIMEOUT``
     * - ``retries``
       - ``-r RETRIES``
     * - ``load_mibs``
       - ``-m MIB[:MIB...]``
     * - ``mib_directories``
       - ``-M DIR[:DIR...]``
     * - ``print_enums_numerically``
       - ``-O e``
     * - ``print_full_oids``
       - ``-O f``
     * - ``print_oids_numerically``
       - ``-O n``


Migration Example
-----------------

Old code (V1.X.X):

.. code-block:: python

     session = Session(
          hostname="example.com",
          version=3,
          remote_port=161,
          timeout=1,
          use_numeric=True
     )

New code (V2.X.X):

.. code-block:: python

     session = Session(
          hostname="example.com",
          version="3",
          port_number="161",
          timeout="1",
          print_oids_numerically=True
     )

or

.. code-block:: python

     session = Session(
          hostname="example.com",
          version=3,
          port_number=161,
          timeout=1,
          print_oids_numerically=True
     )