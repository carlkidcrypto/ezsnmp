Datatypes C++ Module
====================

.. doxygenstruct:: Result
   :project: EzSnmp
   :members:
   :protected-members:
   :private-members:
   :undoc-members:

############################################
Result.converted_value Types and Results
############################################

This section outlines the possible C++ data types that result from the ``converted_value`` member of the ``Result`` struct. The conversion is based on the SNMP ``type`` string. The underlying C++ type is a ``std::variant`` that can hold one of the following types or an error string.

Numeric Types
=============

These SNMP types are converted into their corresponding C++ numeric equivalents. The conversion logic is designed to extract numerical data from common SNMP output formats, such as ``"60000 milli-seconds"`` or ``"up(1)"``.

Integer / Integer32
-------------------
* **SNMP Types**: ``integer``, ``integer32``
* **C++ Type**: ``int32_t`` (signed 32-bit integer)
* **Example Input**: ``"42"`` -> ``42``

Gauge32 / Counter32 / TimeTicks
-------------------------------
* **SNMP Types**: ``gauge32``, ``counter32``, ``timeticks``
* **C++ Type**: ``uint32_t`` (unsigned 32-bit integer)
* **Example Input**: ``"363647793"`` -> ``363647793``

Counter64
---------
* **SNMP Types**: ``counter64``
* **C++ Type**: ``uint64_t`` (unsigned 64-bit integer)
* **Example Input**: ``"18446744073709551615"`` -> ``18446744073709551615``

Byte Vector Types
=================

These types represent raw byte data and are converted into a vector of unsigned characters.

Hex-STRING
----------
* **SNMP Type**: ``hex-string``
* **C++ Type**: ``std::vector<unsigned char>``
* **Description**: Parses a space-separated string of hexadecimal bytes. Each byte must be 1 or 2 hex characters long.
* **Example Input**: ``"80 00 1F 88 04 01 01"`` -> ``{0x80, 0x00, 0x1F, 0x88, 0x04, 0x01, 0x01}``
* **Special Case**: An empty or whitespace-only input string results in an empty vector.

OctetStr
--------
* **SNMP Type**: ``octetstr``
* **C++ Type**: ``std::vector<unsigned char>``
* **Description**: Converts the raw string value directly into a vector of its character bytes.
* **Example Input**: ``"Hello"`` -> ``{'H', 'e', 'l', 'l', 'o'}`` or ``{0x48, 0x65, 0x6c, 0x6c, 0x6f}``

String Types
============

For many SNMP types, the most useful representation is the original string itself. These types are passed through without conversion.

* **SNMP Types**:
    * ``string``
    * ``oid``, ``objid``, ``objidentity``
    * ``ipaddress``, ``network address``
    * ``opaque``
    * ``bitstring``
    * ``nsapaddress``
    * ``traptype``, ``notiftype``
    * ``objgroup``, ``notifgroup``, ``modid``, ``agentcap``, ``modcomp``
    * ``null``
    * ``other``
* **C++ Type**: ``std::string``
* **Description**: The original string value from the ``Result`` is returned as is.
* **Example Input**: ``"1.3.6.1.2.1.1.1.0"`` -> ``"1.3.6.1.2.1.1.1.0"``

Error and Fallback Conditions
=============================

If a conversion fails or the type is unknown, the ``converted_value`` will hold a ``std::string`` describing the issue.

Conversion Error
----------------
* **C++ Type**: ``std::string``
* **Description**: Occurs when a numeric or hex conversion fails due to malformed input. The string will contain a descriptive error message.
* **Example**: ``"Integer Conversion Error: std::invalid_argument"``
* **Example**: ``"Hex-STRING Conversion Error: Malformed hex part 'G0'"``

Unknown Type
------------
* **C++ Type**: ``std::string``
* **Description**: If the SNMP type string does not match any of the known types listed above, a generic fallback message is returned.
* **Value**: ``"Unknown Type Conversion"``