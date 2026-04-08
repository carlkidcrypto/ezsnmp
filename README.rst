=======
EzSnmp
=======

.. list-table::
   :widths: auto

   * - |Python Code Style|
     - |Clang-format Code Style|
     - |Black|
   * - |Clang-format|
     - |Pull Request Sphinx Docs Check|
     - |PyPI Distributions|
   * - |TestPyPI Distributions|
     - |Tests Homebrew|
     - |Tests Native|
   * - |CodeCov|
     - |License|
     - |Build and Publish Docker Images|

.. |Python Code Style| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square
    :target: https://github.com/psf/black
.. |Clang-format Code Style| image:: https://img.shields.io/badge/code%20style-clang--format-brightgreen.svg?style=flat-square
    :target: https://clang.llvm.org/docs/ClangFormat.html
.. |Black| image:: https://img.shields.io/github/actions/workflow/status/carlkidcrypto/ezsnmp/black.yml?style=flat-square&label=Black
    :target: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/black.yml
.. |Clang-format| image:: https://img.shields.io/github/actions/workflow/status/carlkidcrypto/ezsnmp/clang_format.yml?style=flat-square&label=Clang-format
    :target: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/clang_format.yml
.. |Pull Request Sphinx Docs Check| image:: https://img.shields.io/github/actions/workflow/status/carlkidcrypto/ezsnmp/sphinx_build.yml?style=flat-square&label=Sphinx+Docs+Check
    :target: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/sphinx_build.yml
.. |PyPI Distributions| image:: https://img.shields.io/github/actions/workflow/status/carlkidcrypto/ezsnmp/build_and_publish_to_pypi.yml?style=flat-square&label=PyPI+Distributions
    :target: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/build_and_publish_to_pypi.yml
.. |TestPyPI Distributions| image:: https://img.shields.io/github/actions/workflow/status/carlkidcrypto/ezsnmp/build_and_publish_to_test_pypi.yml?style=flat-square&label=TestPyPI+Distributions
    :target: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/build_and_publish_to_test_pypi.yml
.. |Tests Homebrew| image:: https://img.shields.io/github/actions/workflow/status/carlkidcrypto/ezsnmp/tests_homebrew.yml?style=flat-square&label=Tests+Homebrew
    :target: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/tests_homebrew.yml
.. |Tests Native| image:: https://img.shields.io/github/actions/workflow/status/carlkidcrypto/ezsnmp/tests_native.yml?style=flat-square&label=Tests+Native
    :target: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/tests_native.yml
.. |CodeCov| image:: https://img.shields.io/codecov/c/github/carlkidcrypto/ezsnmp/main?style=flat-square&label=CodeCov
    :target: https://codecov.io/gh/carlkidcrypto/ezsnmp
.. |License| image:: https://img.shields.io/badge/license-BSD-blue.svg?style=flat-square
    :target: https://github.com/carlkidcrypto/ezsnmp/blob/main/LICENSE
.. |Build and Publish Docker Images| image:: https://img.shields.io/github/actions/workflow/status/carlkidcrypto/ezsnmp/build_and_publish_docker_images.yml?style=flat-square&label=Build+Docker+Images
    :target: https://github.com/carlkidcrypto/ezsnmp/actions/workflows/build_and_publish_docker_images.yml

.. image:: https://github.com/carlkidcrypto/ezsnmp/blob/main/images/ezsnmp_logo.jpeg
    :alt: EzSnmp Logo

Introduction
------------

EzSnmp is a fork of `Easy SNMP <https://github.com/easysnmp/easysnmp>`__

Why Another Library?
--------------------

- Simple, because the maintainer of `Easy SNMP` seems to have abandoned the project or isn't actively working on it.
- This version (EzSnmp) will attempt to remain up to date with Python versions that are supported by `Python <https://devguide.python.org/versions/>`__
  and net-snmp versions that are supported by `Net-SNMP <https://www.net-snmp.org/download.html>`__


How to Support This Project?
----------------------------

.. image:: https://github.com/carlkidcrypto/ezsnmp/blob/main/images/buy_me_a_coffee.png
    :alt: Buy Me A Coffee. 

`Use this link to buy me a coffee! <https://www.buymeacoffee.com/carlkidcrypto>`__

Getting Started
---------------
Please check out the `EzSnmp documentation <https://carlkidcrypto.github.io/ezsnmp/>`_. This includes installation
instructions for various operating systems.

Code Coverage
-------------

EzSnmp uses `CodeCov <https://codecov.io/gh/carlkidcrypto/ezsnmp>`_ for tracking code coverage across both Python and C++ components. 

Coverage reports are automatically generated and uploaded for:

- **Python tests**: Coverage from pytest runs (both Docker and native environments)
- **C++ tests**: Coverage from Google Test runs using lcov (both Docker and native environments)

Coverage data is collected from multiple test workflows:

- Docker-based Python tests across multiple distributions
- Native Python tests on Ubuntu and macOS
- Docker-based C++ tests
- Native C++ tests on Ubuntu and macOS

You can view the latest coverage reports and trends at the `CodeCov dashboard <https://codecov.io/gh/carlkidcrypto/ezsnmp>`_.

Want to Contribute?
-------------------

Check out the development guide at `EzSnmp Development <https://carlkidcrypto.github.io/ezsnmp/html/development.html>`_.


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
- **Kent Coble**: who was the most recent maintainer. `Easy SNMP <https://github.com/easysnmp/easysnmp>`_

License
-------

EzSnmp is released under the **BSD** license. Please see the
`LICENSE <LICENSE>`_
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

Copyright (c) 2024-2026 carlkidcrypto All Rights Reserved. This program is
free software; you can redistribute it and/or modify it under the same
terms as Net-SNMP itself.

----

.. note::
   This content was generated by AI and reviewed by humans. Mistakes may still occur. PRs for corrections are welcome.