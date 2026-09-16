SessionBase C++ Module
======================


Analysis of Snmpwalk Options and SessionBase Constructor Mapping
=================================================================

This document analyzes how the command-line options of the ``snmpwalk`` tool
correspond to the parameters of the ``SessionBase`` C++ constructor.  It
identifies direct matches, options without direct counterparts, and implicit or
default behaviors. Note this behavior is identical/very similar for the other
supported methods like ``snmpget``, ``snmpbulkwalk``, etc.

Direct Mappings
---------------

Several ``snmpwalk``, ``snmpget``, ``etc..`` options have direct equivalents in the ``SessionBase``
constructor:

* ``-v 1|2c|3`` -> ``version``
* ``-c COMMUNITY`` -> ``community``
* ``-a PROTOCOL`` -> ``auth_protocol``
* ``-A PASSPHRASE`` -> ``auth_passphrase``
* ``-e ENGINE-ID`` -> ``security_engine_id``
* ``-E ENGINE-ID`` -> ``context_engine_id``
* ``-l LEVEL`` -> ``security_level``
* ``-n CONTEXT`` -> ``context``
* ``-u USER-NAME`` -> ``security_username``
* ``-x PROTOCOL`` -> ``privacy_protocol``
* ``-X PASSPHRASE`` -> ``privacy_passphrase``
* ``-Z BOOTS,TIME`` -> ``boots_time``
* ``-r RETRIES`` -> ``retries``
* ``-t TIMEOUT`` -> ``timeout``
* ``AGENT`` (hostname) -> ``hostname``

The ``[OID]`` argument given to ``snmpwalk`` specifies the target OID for the
walk.  While not a parameter of the ``SessionBase`` *constructor*, it
represents the *action* to be performed. ``SessionBase`` sets up a session,
and contains a ``walk`` method that then uses the OID as its input parameter.


No Direct Mapping (or Implicit/Default)
----------------------------------------

The following ``snmpwalk`` options do *not* correspond to ``SessionBase``
constructor parameters:

* ``-h, --help``, ``-H``, ``-V, --version``, ``-d``, ``-D[TOKEN[,...]]``,
  ``-m MIB[:...]``, ``-M DIR[:...]``, ``-P MIBOPTS``, ``-O OUTOPTS``,
  ``-I INOPTS``, ``-L LOGOPTS``, ``-C APPOPTS``

These options influence ``snmpwalk``'s operation (help, version display,
debugging, MIB loading, output format, etc.). They are handled by the lower
level ``NetsnmpBase`` functions. The ``SessionBase`` constructor is designed
for core SNMP session setup, not the specifics of the ``snmpwalk`` tool or
other SNMP operations.

The ``port_number`` parameter in the ``SessionBase`` constructor has no
direct equivalent in ``snmpwalk``. ``snmpwalk`` defaults to the standard
SNMP port (161).  The constructor parameter allows overriding this, but this
cannot be set through ``snmpwalk``'s options.

Summary Table
-------------

.. csv-table::
   :header-rows: 1

   "snmpwalk Option", "SessionBase Parameter", "Direct Map?", "Notes"
   "-v 1|2c|3", "version", "Yes", "-v followed by the version (1, 2c, or 3)"
   "-c COMMUNITY", "community", "Yes", ""
   "-a PROTOCOL", "auth_protocol", "Yes", ""
   "-A PASSPHRASE", "auth_passphrase", "Yes", ""
   "-e ENGINE-ID", "security_engine_id", "Yes", ""
   "-E ENGINE-ID", "context_engine_id", "Yes", ""
   "-l LEVEL", "security_level", "Yes", ""
   "-n CONTEXT", "context", "Yes", ""
   "-u USER-NAME", "security_username", "Yes", ""
   "-x PROTOCOL", "privacy_protocol", "Yes", ""
   "-X PASSPHRASE", "privacy_passphrase", "Yes", ""
   "-Z BOOTS,TIME", "boots_time", "Yes", ""
   "-r RETRIES", "retries", "Yes", ""
   "-t TIMEOUT", "timeout", "Yes", ""
   "AGENT (hostname)", "hostname", "Yes", ""
   "[OID]", "(N/A - Action)", "No", "OID is the target of methods like walk, bulk_walk, get, etc., and is not a constructor parameter."
   "port_number", "port_number", "No (Implicit)", "snmpwalk and methods alike use the default port 161. Parameter allows overriding."
   "All other options", "(N/A - Tool Options)", "No", "These control snmpwalk's and methods alike behavior, not the core SessionBase. If one wants more control, use the NetSnmpBase functions."


.. doxygenclass:: SessionBase
  :project: EzSnmp
  :members:
  :private-members:
  :undoc-members:
  :protected-members: