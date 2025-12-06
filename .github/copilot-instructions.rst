==========================================
GitHub Copilot Code Review Instructions
==========================================

Review Philosophy
=================

- Only comment when you have HIGH CONFIDENCE (>80%) that an issue exists
- Be concise: one sentence per comment when possible
- Focus on actionable feedback, not observations
- When reviewing text, only comment on clarity issues if the text is genuinely confusing or could lead to errors. "Could be clearer" is not the same as "is confusing" - stay silent unless HIGH confidence it will cause problems

Priority Areas (Review These)
==============================

Security & Safety
-----------------

- Unsafe code blocks without justification
- Command injection risks (shell commands, user input)
- Path traversal vulnerabilities
- Credential exposure or hardcoded secrets (SNMP community strings, v3 credentials)
- Missing input validation on external data (OIDs, SNMP responses)
- Improper error handling that could leak sensitive info
- SNMP v3 authentication/privacy implementation issues

Correctness Issues
------------------

- Logic errors that could cause crashes or incorrect SNMP operations
- Race conditions in async code or C++ threading
- Resource leaks (files, connections, memory, Net-SNMP sessions)
- Off-by-one errors or boundary conditions in OID parsing
- Memory management issues in C++ extensions (leaks, double-frees)
- Incorrect error propagation between C++ and Python layers
- SWIG interface issues that could cause segfaults
- Net-SNMP API misuse or incorrect session handling
- Overly defensive code that adds unnecessary checks
- Unnecessary comments that just restate what the code already shows (remove them)

Architecture & Patterns
-----------------------

- Code that violates existing patterns in the codebase
- Missing error handling in C++ or Python layers
- Improper SWIG interface definitions
- Breaking changes to the Python API without justification
- Incorrect use of Net-SNMP data structures

Project-Specific Context
=========================

- This is a Python/C++ SNMP library project using Net-SNMP
- Core components:

  - ``ezsnmp/``: Python API layer (session.py, datatypes.py, exceptions.py)
  - ``ezsnmp/src/``: C++ implementation (SessionBase, NetSnmpBase, etc.)
  - ``ezsnmp/interface/``: SWIG interface files (.i files)
  - ``python_tests/``: Python test suite using pytest
  - ``cpp_tests/``: C++ test suite using Catch2/Meson

- Error handling: C++ exceptions should be caught and converted to Python exceptions
- Memory management: Follow Net-SNMP memory management patterns (free what you allocate)
- See ``HOWTOAI.rst`` for AI-assisted code standards
- SNMP v3 authentication/privacy code requires extra scrutiny

CI Pipeline Context
===================

**Important**: You review PRs immediately, before CI completes. Do not flag issues that CI will catch.

What Our CI Checks
------------------

**Python formatting:**

- ``black`` - Python code formatting (via ``.github/workflows/black.yml``)

**C++ formatting:**

- ``clang-format`` - C++ code formatting (via ``.github/workflows/clang_format.yml``)

**Testing:**

- ``pytest python_tests/`` - Python test suite (via ``tests_native.yml``, ``tests_homebrew.yml``, etc.)
- C++ tests via Meson (via ``tests_cpp_native.yml``, ``tests_docker_cpp_tests.yml``)
- Integration tests (via ``integration_tests.yml``)

**Documentation:**

- Sphinx documentation build (via ``sphinx_build.yml``)

**Setup steps CI performs:**

- Installs Net-SNMP via native package managers (apt, brew, port)
- Installs Python dependencies via pip
- Builds C++ extensions via ``setup.py build_ext``
- Runs SWIG to generate Python bindings

**Key insight**: Don't flag issues that the CI checks will catch (formatting, test failures, build errors).

Skip These (Low Value)
======================

Do not comment on:

- **Style/formatting** - CI handles this (black, clang-format)
- **Test failures** - CI handles this (full test suite)
- **Missing dependencies** - CI handles this (build will fail)
- **Minor naming suggestions** - unless truly confusing
- **Suggestions to add comments** - for self-documenting code
- **Refactoring suggestions** - unless there's a clear bug or maintainability issue
- **Multiple issues in one comment** - choose the single most critical issue
- **Logging suggestions** - unless for errors or security events
- **Pedantic accuracy in text** - unless it would cause actual confusion or errors

Response Format
===============

When you identify an issue:

1. **State the problem** (1 sentence)
2. **Why it matters** (1 sentence, only if not obvious)
3. **Suggested fix** (code snippet or specific action)

Example::

    This could cause a segfault if the Net-SNMP session is NULL. 
    Add a null check before dereferencing: if (!session) { throw std::runtime_error("Session is null"); }

When to Stay Silent
===================

If you're uncertain whether something is an issue, don't comment. False positives create noise and reduce trust in the review process.

----

This content was generated by AI and reviewed by humans. Mistakes may still occur. PRs for corrections are welcome.
