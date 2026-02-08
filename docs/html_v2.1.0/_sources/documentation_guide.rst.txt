====================
Documentation Guide
====================

Overview
========

EzSnmp documentation is organized across multiple files and directories to provide
comprehensive information for different audiences and use cases.

Documentation Structure
=======================

Repository Documentation
------------------------

**Main README** (``README.rst``)
    The main project README provides:
    
    * Project overview and introduction
    * Why EzSnmp was created
    * Links to documentation
    * How to support the project
    * License and copyright information
    * Acknowledgments

**Directory READMEs**
    Each major directory contains its own README.rst:
    
    * ``cml_tests/README.rst`` - CML testing overview
    * ``cpp_tests/README.rst`` - C++ unit tests documentation
    * ``python_tests/README.rst`` - Python test suite with setup instructions
    * ``ezsnmp/README.rst`` - Source code structure and build process
    * ``images/README.rst`` - Image assets documentation
    * ``integration_tests/README.rst`` - Integration test scenarios
    * ``docker/*/README.rst`` - Docker container documentation for each platform

Sphinx Documentation
--------------------

The Sphinx documentation (this site) provides:

**Getting Started**
    * Installation instructions for multiple platforms
    * Quick start examples
    * Session configuration examples
    * Exception handling guide

**API Reference**
    * Python class documentation
    * C++ class documentation (via Doxygen/Breathe)
    * SWIG interface documentation

**Guides**
    * :doc:`migration_guide` - Migrating from v1.x to v2.x
    * :doc:`development` - Development and contribution guide

Building Documentation
======================

Doxygen Documentation
---------------------

Doxygen generates C++ API documentation from source code comments.

Build doxygen documentation:

.. code-block:: bash

    cd /path/to/ezsnmp
    rm -rf doxygen_docs_build/
    mkdir doxygen_docs_build
    doxygen .doxygen

The XML output will be generated in ``doxygen_docs_build/doxygen/xml/``.

**Important**: Doxygen must be run **before** building Sphinx documentation,
as Sphinx uses the Breathe extension to integrate the doxygen XML files.

Sphinx Documentation
--------------------

Sphinx builds the HTML documentation from reStructuredText (.rst) files.

Prerequisites:

.. code-block:: bash

    cd sphinx_docs_build
    pip install -r requirements.txt

Build process:

.. code-block:: bash

    # 1. First build doxygen (see above)
    cd /path/to/ezsnmp
    mkdir doxygen_docs_build
    doxygen .doxygen
    
    # 2. Then build sphinx
    cd sphinx_docs_build
    mkdir -p source/_static source/_templates
    make clean
    make html

The HTML output will be in ``docs/html/``.

Documentation Workflow
======================

For Contributors
----------------

When contributing to EzSnmp:

1. **Update relevant README files** if you add new directories or major features
2. **Add docstrings** to Python code following existing style
3. **Add Doxygen comments** to C++ code using standard Doxygen format
4. **Update .rst files** if you change APIs or add major functionality
5. **Rebuild documentation** locally to verify your changes

Adding New Documentation
------------------------

To add new documentation pages:

1. Create a new ``.rst`` file in ``sphinx_docs_build/source/``
2. Add appropriate reStructuredText content
3. Include the file in an appropriate toctree (usually in ``modules.rst``)
4. Rebuild documentation to verify

Documentation Standards
=======================

reStructuredText Guidelines
---------------------------

* Use descriptive section headers with proper underlining
* Include code blocks with appropriate language tags
* Use relative links for internal documentation
* Add alt text to all images
* Keep line length reasonable (80-100 characters)

Code Documentation
------------------

**Python:**
    * Use Google-style or NumPy-style docstrings
    * Document all public classes, methods, and functions
    * Include parameter types and return types
    * Provide usage examples where helpful

**C++:**
    * Use Doxygen comment style (``/** ... */`` or ``///``)
    * Document all public classes, methods, and functions
    * Use ``@param``, ``@return``, ``@throws`` tags
    * Include brief and detailed descriptions

Link Guidelines
---------------

* Use **relative links** for files within the repository
* Use **descriptive link text** (not "click here")
* Verify all links work before committing
* Update links if files are moved or renamed

Checking Documentation
======================

Before committing documentation changes:

.. code-block:: bash

    # Build doxygen
    doxygen .doxygen
    
    # Build sphinx
    cd sphinx_docs_build
    make clean
    make html
    
    # Check for warnings
    # Sphinx will show warnings for:
    # - Broken links
    # - Missing files
    # - Invalid syntax
    # - Missing references

View the generated HTML in ``docs/html/index.html`` to verify:

* All pages render correctly
* Links work properly
* Code examples display properly
* Images appear correctly
* Table of contents is accurate

Resources
=========

* `reStructuredText Primer <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_
* `Sphinx Documentation <https://www.sphinx-doc.org/>`_
* `Doxygen Manual <https://www.doxygen.nl/manual/>`_
* `Breathe Documentation <https://breathe.readthedocs.io/>`_

Related Documentation
=====================

* :doc:`development` - Development guide
* :doc:`migration_guide` - Migration guide
* `GitHub Repository <https://github.com/carlkidcrypto/ezsnmp>`_
