====================================
How to Use AI with ezsnmp
====================================

*A practical guide for contributing to ezsnmp using AI coding assistants*

ezsnmp benefits from thoughtful AI-assisted development, but contributors must maintain high standards for code quality, security, and collaboration. Whether you use GitHub Copilot, Cursor, Claude, or other AI tools, this guide will help you contribute effectively.

----

Core Principles
===============

- **Human Oversight**: You are accountable for all code you submit. Never commit code you don't understand or can't maintain.
- **Quality Standards**: AI code must meet the same standards as human written code—tests, docs, and patterns included.
- **Transparency**: Be open about significant AI usage in PRs and explain how you validated it.

----

Best Practices
==============

✅ Recommended Uses
-------------------

- Generating boilerplate code and test fixtures
- Creating comprehensive test suites for Python and C++ code
- Writing documentation (README.rst, Sphinx docs, Doxygen comments)
- Refactoring existing code for clarity
- Generating utility functions and type hints
- Explaining Net-SNMP API usage and patterns
- Converting between SNMP data types

❌ Avoid AI For
---------------

- Low-level C++ SNMP protocol implementation without thorough review
- Memory management in C++ extensions
- Security-critical SNMP credential handling (v3 auth/priv)
- Code you don't fully understand
- Large architectural changes to the C++/Python interface
- SWIG interface file modifications without testing

Workflow Tips
-------------

- Start small and validate often. Build, format, and test incrementally
- Study existing patterns in both Python and C++ layers
- Always ask: "Is this secure? Does it handle SNMP errors properly? What edge cases need testing?"
- Test on multiple platforms (Linux, macOS) when modifying C++ code

Security Considerations
-----------------------

- Extra review required for SNMP v3 authentication/privacy code, credential handling, and network operations
- Never expose SNMP community strings or credentials in prompts or test files
- Validate all OID inputs to prevent injection attacks
- Follow ezsnmp's existing security patterns for credential management

----

Testing & Review
================

Before submitting AI assisted code, confirm that:

- You understand every line (both Python and C++ if applicable)
- All tests pass locally: ``pytest python_tests/``, C++ tests in ``cpp_tests/``
- Code is formatted: ``black`` for Python, ``clang-format`` for C++
- Docs are updated: README.rst, Sphinx docs, and Doxygen comments
- Code follows existing patterns in both languages

**Always get human review** for:

- Security sensitive code (SNMP v3 credentials, authentication)
- Core architecture changes to SessionBase or NetSnmpBase
- C++ extension modifications and SWIG interface changes
- SNMP protocol implementations
- Memory management in C++ code
- Large refactors or anything you're unsure about

----

Working with AI on ezsnmp
==========================

- Be careful with sensitive data in prompts (SNMP community strings, test credentials)
- Provide context about the dual Python/C++ nature of the project
- When working on C++ extensions, mention you're using SWIG for Python bindings
- Specify which layer you're working on: Python API, C++ bindings, or Net-SNMP interface
- Use AI to help understand Net-SNMP documentation and API patterns

----

Community & Collaboration
==========================

- In PRs, note significant AI use and how you validated results
- Share prompting tips, patterns, and pitfalls
- Be responsive to feedback and help improve this guide

----

Remember
========

AI is a powerful assistant, not a replacement for your judgment. Use it to speed up development while keeping your brain engaged, your standards high, and ezsnmp secure.

Questions? Open an issue or PR on `GitHub <https://github.com/carlkidcrypto/ezsnmp>`_ to discuss AI-assisted development practices.

----

Getting Started with AI Tools
==============================

Quick Setup
-----------

**Using GitHub Copilot:**

- Install the `GitHub Copilot extension <https://marketplace.visualstudio.com/items?itemName=GitHub.copilot>`_ for VS Code
- Enable Copilot for Python and C++ files in your settings
- Recommended extensions:

  - `Python extension <https://marketplace.visualstudio.com/items?itemName=ms-python.python>`_ for Python support
  - `C/C++ extension <https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools>`_ for C++ IntelliSense
  - `clangd <https://marketplace.visualstudio.com/items?itemName=llvm-vs-code-extensions.vscode-clangd>`_ for better C++ intelligence

**Using Cursor:**

- Download `Cursor <https://cursor.sh/>`_ (VS Code fork with built-in AI)
- Open the ezsnmp repository
- Use Cmd/Ctrl+K for inline AI editing, Cmd/Ctrl+L for chat

**Using Claude or ChatGPT:**

- Copy relevant code sections into the chat interface
- Provide context about the ezsnmp architecture (see below)
- Always test generated code locally before committing

Python/C++ Configuration
------------------------

Configure your AI tool to help with the hybrid Python/C++ codebase:

**VS Code settings.json:**

.. code-block:: json

    {
      "python.formatting.provider": "black",
      "python.linting.enabled": true,
      "python.testing.pytestEnabled": true,
      "python.testing.pytestArgs": ["python_tests"],
      "[cpp]": {
        "editor.defaultFormatter": "llvm-vs-code-extensions.vscode-clangd"
      },
      "github.copilot.enable": {
        "python": true,
        "cpp": true
      }
    }

**Cursor Rules (.cursorrules in repo root):**

.. code-block:: text

    This is a Python/C++ SNMP library project using Net-SNMP.
    - Python code: Follow PEP 8, use black formatter, add type hints
    - C++ code: Use C++17, follow clang-format style, add Doxygen comments
    - SWIG interface files (.i): Handle memory management carefully
    - Test all changes in python_tests/ and cpp_tests/
    - Run black and clang-format before committing

----

Understanding ezsnmp's Architecture
====================================

New to SNMP or Python C++ extensions? Here are key questions to ask your AI tool:

Essential Concepts
------------------

**"Explain ezsnmp's structure"**

Ask: "I'm looking at the ezsnmp repository. Can you explain the purpose of each main directory and how Python and C++ layers interact?"

Key insights:

- **ezsnmp/**: Python API layer (session.py, datatypes.py, exceptions.py)
- **ezsnmp/src/**: C++ implementation (SessionBase, NetSnmpBase, etc.)
- **ezsnmp/interface/**: SWIG interface files (.i) that bridge Python and C++
- **python_tests/**: Python test suite using pytest
- **cpp_tests/**: C++ test suite using Catch2 or similar
- **setup.py**: Build script that compiles C++ extensions and runs SWIG

**"How does SNMP communication work in ezsnmp?"**

Ask: "What is SNMP and how does ezsnmp wrap the Net-SNMP C library? Show me an example from ezsnmp/session.py"

Key insights:

- ezsnmp wraps Net-SNMP's C API using C++ classes
- SWIG generates Python bindings for C++ classes
- Session classes handle SNMP GET, SET, WALK, and BULK operations
- Supports SNMP v1, v2c, and v3 (with authentication/privacy)

**"What's the request/response flow?"**

Ask: "Walk me through what happens when I call session.get('1.3.6.1.2.1.1.1.0') in Python"

Key insight: Python call → SWIG wrapper → C++ SessionBase → Net-SNMP C API → Network → Response parsing → Python object

Navigating the Codebase with AI
--------------------------------

**Finding the right file:**

Ask: "I want to understand how SNMP GET requests work. Which files should I read?"

AI might suggest:

- Python layer: ``ezsnmp/session.py`` (Session.get method)
- C++ layer: ``ezsnmp/src/sessionbase.cpp`` (SessionBase::get_list)
- SWIG interface: ``ezsnmp/interface/sessionbase.i``

**Understanding patterns:**

Ask: "Show me the pattern for adding a new SNMP data type to ezsnmp"

Then: "How does error handling work between C++ exceptions and Python exceptions?"

----

Practical Examples
==================

Example 1: Adding a New SNMP Data Type
---------------------------------------

**Scenario:** You want to add support for a new SNMP data type.

**Step 1 - Explore existing data types:**

.. code-block:: bash

    # Ask AI: "Show me how ezsnmp handles SNMP data types"
    # Look at the Python layer
    cat ezsnmp/datatypes.py

    # Look at the C++ layer
    cat ezsnmp/src/datatypes.cpp

**Step 2 - Ask AI to draft the new type:**

.. code-block:: text

    Prompt: "I want to add support for SNMP Opaque data type in ezsnmp. 
    Based on the pattern for Counter64 in datatypes.py and datatypes.cpp, 
    draft the implementation for both Python and C++ layers."

**Step 3 - Validate with AI:**

.. code-block:: text

    Ask: "Review this code for:
    1. Proper type conversions between Net-SNMP, C++, and Python
    2. Memory management in C++ (no leaks)
    3. SWIG interface file updates needed
    4. Test coverage for edge cases"

**Step 4 - Test locally:**

.. code-block:: bash

    # Build the extension
    python setup.py build_ext --inplace

    # Run Python tests
    pytest python_tests/test_datatypes.py -v

    # Run C++ tests
    cd cpp_tests && meson test

Example 2: Fixing a C++ Compilation Error
------------------------------------------

**Scenario:** You're getting a Net-SNMP API error or memory issue.

**Step 1 - Copy the full error:**

.. code-block:: bash

    python setup.py build_ext --inplace 2>&1 | clip  # Windows
    python setup.py build_ext --inplace 2>&1 | pbcopy  # macOS

**Step 2 - Ask AI with context:**

.. code-block:: text

    Prompt: "I'm getting this C++ compilation error in ezsnmp:

    [paste error]

    Here's the relevant code from ezsnmp/src/sessionbase.cpp:
    [paste code section]

    This code interfaces with Net-SNMP C API. Explain what's wrong 
    and how to fix it following Net-SNMP best practices."

**Step 3 - Understand the fix:**

.. code-block:: text

    Ask: "Explain why this fix works and what I should know about 
    Net-SNMP memory management and session handling"

**Step 4 - Apply and verify:**

.. code-block:: bash

    # Apply the fix and rebuild
    python setup.py build_ext --inplace

    # Run all tests
    pytest python_tests/
    cd cpp_tests && meson test

    # Format code
    black ezsnmp/
    clang-format -i ezsnmp/src/*.cpp ezsnmp/include/*.h

Example 3: Adding a New Session Method
---------------------------------------

**Scenario:** You want to add a new SNMP operation method to the Session class.

**Step 1 - Study existing methods:**

.. code-block:: bash

    # Ask AI: "How does ezsnmp implement SNMP GET?"
    # Look at Python API
    cat ezsnmp/session.py | grep -A 20 "def get"

    # Look at C++ implementation
    cat ezsnmp/src/sessionbase.cpp | grep -A 30 "get_list"

**Step 2 - Ask AI to draft the implementation:**

.. code-block:: text

    Prompt: "I want to add a 'get_bulk_repeaters' method to ezsnmp Session class 
    that allows specifying different max-repetitions for different OIDs. 
    Based on the existing get() and bulkwalk() patterns, draft:
    1. The Python Session method in session.py
    2. The C++ SessionBase method in src/sessionbase.cpp
    3. The SWIG interface declaration in interface/sessionbase.i"

**Step 3 - Add tests and documentation:**

.. code-block:: text

    Ask: "Generate pytest tests for this new method covering:
    1. Success cases with various OID patterns
    2. Error cases (invalid OIDs, timeouts, SNMP errors)
    3. SNMP v1, v2c, and v3 compatibility
    Also draft Sphinx documentation for the docstring."

**Step 4 - Implement with validation:**

.. code-block:: bash

    # Make changes to all three layers
    # Rebuild
    python setup.py build_ext --inplace

    # Run tests
    pytest python_tests/test_session.py::test_get_bulk_repeaters -v

    # Run full test suite
    pytest python_tests/
    cd cpp_tests && meson test

    # Update documentation
    cd sphinx_docs_build && make html

----

This content was generated by AI and reviewed by humans. Mistakes may still occur. PRs for corrections are welcome.
