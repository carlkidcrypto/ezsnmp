Exceptions Python Module
========================

Differences between V1.X.X and V2.X.X of the EzSnmp Exception Handling

The primary difference between V1.X.X and V2.X.X lies in how exceptions are structured and handled.

* **Base Exception Class:**

    * **V1.X.X:** Uses ``EzSNMPError`` as the base exception class. Specific error types inherit from this 
      class (e.g., ``EzSNMPConnectionError``, ``EzSNMPTimeoutError``).
    * **V2.X.X:** Uses ``GenericError`` as the base exception class. All other exceptions inherit from 
      ``GenericError``.

* **Specific Exception Classes:**

    * **V1.X.X:** Defines individual exception classes for various EzSnmp errors, such as 
      ``EzSNMPConnectionError``, ``EzSNMPTimeoutError``, ``EzSNMPUnknownObjectIDError``, 
      ``EzSNMPNoSuchNameError``, ``EzSNMPNoSuchObjectError``, ``EzSNMPNoSuchInstanceError``, and 
      ``EzSNMPUndeterminedTypeError``.
    * **V2.X.X:** While retaining many of the same error types (``ConnectionError``, ``NoSuchInstanceError``, 
      ``NoSuchNameError``, ``NoSuchObjectError``, ``TimeoutError``, ``UndeterminedTypeError``, 
      ``UnknownObjectIDError``), V2.X.X adds new ones related to packet and parsing errors: ``PacketError`` and 
      ``ParseError``. Crucially, all inherit from ``GenericError``.

* **Error Handling:**

    * **V1.X.X:** Implicit exception handling. The code relies on catching specific exception types.
    * **V2.X.X:** Introduces ``_handle_error(e)``. This function maps exceptions from the lower-level C++ 
      net-snmp wrapper (e.g., ``ConnectionErrorBase``) to the corresponding Python exception classes. This 
      provides a cleaner Python interface, abstracting C++ error types.

In summary, V2.X.X offers a more robust and structured approach. ``_handle_error`` for mapping C++ exceptions 
improves usability and maintainability. The common base class (``GenericError``) and more specific exception 
types facilitate organized error handling. The addition of ``PacketError`` and ``ParseError`` enhances error 
reporting.

.. automodule:: ezsnmp.exceptions
   :no-index:

.. autoclass:: ezsnmp.exceptions.ConnectionError
    :members:
    :undoc-members:
    :show-inheritance:
    :special-members: __init__

.. autoclass:: ezsnmp.exceptions.GenericError
    :members:
    :undoc-members:
    :show-inheritance:
    :special-members: __init__

.. autoclass:: ezsnmp.exceptions.NoSuchInstanceError
    :members:
    :undoc-members:
    :show-inheritance:
    :special-members: __init__

.. autoclass:: ezsnmp.exceptions.NoSuchNameError 
    :members:
    :undoc-members:
    :show-inheritance:
    :special-members: __init__

.. autoclass:: ezsnmp.exceptions.NoSuchObjectError
    :members:
    :undoc-members:
    :show-inheritance:
    :special-members: __init__

.. autoclass:: ezsnmp.exceptions.PacketError
    :members:
    :undoc-members:
    :show-inheritance:
    :special-members: __init__

.. autoclass:: ezsnmp.exceptions.ParseError
    :members:
    :undoc-members:
    :show-inheritance:
    :special-members: __init__

.. autoclass:: ezsnmp.exceptions.TimeoutError
    :members:
    :undoc-members:
    :show-inheritance:
    :special-members: __init__

.. autoclass:: ezsnmp.exceptions.UndeterminedTypeError
    :members:
    :undoc-members:
    :show-inheritance:
    :special-members: __init__

.. autoclass:: ezsnmp.exceptions.UnknownObjectIDError
    :members:
    :undoc-members:
    :show-inheritance:
    :special-members: __init__

.. autofunction:: ezsnmp.exceptions._handle_error