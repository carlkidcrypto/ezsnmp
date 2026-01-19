Development Guide
=================

How to Generate the Sphinx Documentation
----------------------------------------

.. note::
   Documentation is automatically built and deployed to GitHub Pages when changes are pushed to the main branch.
   Current build outputs are not committed to the repository to avoid bloat and merge conflicts.
   However, versioned documentation folders (``docs/html_v1.1.0/``, ``docs/html_v2.0.1/``, etc.) are kept in the repository for historical reference.

For local documentation builds, first run doxygen to generate the XML files needed by Breathe.

.. code-block:: bash

    rm -drf doxygen_docs_build/ html/ latex/ && mkdir doxygen_docs_build && doxygen .doxygen

Next you may generate the documentation as follows:

.. code:: bash

    # Install Sphinx
    # See this website for install instructions https://www.sphinx-doc.org/en/master/usage/installation.html

    # Build the documentation into static HTML pages
    cd sphinx_docs_build
    python3 -m pip install -r requirements.txt
    make html

The generated documentation will be built into the ``docs/`` directory. The current build outputs (``docs/html/``, ``docs/_static/``, etc.) are ignored by git, but versioned documentation folders are kept for historical reference.
The documentation is automatically deployed to https://carlkidcrypto.github.io/ezsnmp/ via GitHub Actions.

Making The SWIG Interface Files
-------------------------------

First look for the netsnmp app file under <https://github.com/net-snmp/net-snmp/tree/5e691a85bcd95a42872933515698309e57832cfc/apps>

Two copy the c file over, for example `snmpwalk.c`. Then rename to change the extension to `.cpp`.

Three make a header file for it `snmpwalk.h` and extract methods/functions from the source code.

Four run the command below to generate the wrap file.

.. code-block:: bash

    swig -c++ -python -builtin -threads -doxygen -std=c++17 -outdir ezsnmp/. -o ezsnmp/src/ezsnmp_netsnmpbase.cpp ezsnmp/interface/netsnmpbase.i &&
    swig -c++ -python -builtin -threads -doxygen -std=c++17 -outdir ezsnmp/. -o ezsnmp/src/ezsnmp_sessionbase.cpp ezsnmp/interface/sessionbase.i &&
    swig -c++ -python -builtin -threads -doxygen -std=c++17 -outdir ezsnmp/. -o ezsnmp/src/ezsnmp_datatypes.cpp ezsnmp/interface/datatypes.i &&
    swig -c++ -python -builtin -threads -doxygen -std=c++17 -outdir ezsnmp/. -o ezsnmp/src/ezsnmp_exceptionsbase.cpp ezsnmp/interface/exceptionsbase.i


* `-c++` to force generation of a `.cpp` file
* `-python` to build a python module
* `-builtin` to build with native python data types. `Python_builtin_types <https://swig.org/Doc4.0/Python.html#Python_builtin_types>`_
* `-doxygen` Convert C++ doxygen comments to pydoc comments in proxy classes `Python_commandline <https://swig.org/Doc4.0/Python.html#Python_commandline>`_
* `-threads` adds thread support for all modules. `Support for Multithreaded Applications <https://swig.org/Doc4.0/Python.html#Support_for_Multithreaded_Applications>`_

Five run

.. code-block:: bash

    clear && rm -drf build ezsnmp.egg-info && python3 -m pip install .

Six run it in python3

.. code-block:: bash

    python3
    >>> import ezsnmp
    >>> args = ["-v" , "3", "-u", "secondary_sha_aes", "-a", "SHA", "-A", "auth_second", "-x", "AES", "-X" ,"priv_second", "-l", "authPriv", "localhost:11161"]
    >>> retval = ezsnmp.snmpwalk(args)
    >>> print(retval)

Making The Patch Files
----------------------

Within the patches directory run the following command.

.. code-block:: bash

    diff -Naurw ~/Downloads/net-snmp-master/apps/snmpwalk.c ../src/snmpwalk.cpp > snmpwalk.patch

Running Tests
-------------

Python Tests
~~~~~~~~~~~~

Tests use `Pytest <https://github.com/pytest-dev/pytest>`_. You can run
them with the following on Linux:

.. code:: bash

    git clone https://github.com/carlkidcrypto/ezsnmp.git;
    cd ezsnmp;
    sudo apt update && sudo apt upgrade -y;
    sudo apt install -y snmp snmpd libsnmp-dev libperl-dev snmp-mibs-downloader valgrind;
    sudo apt install -y python3-pip python3-dev  python3-setuptools gdb -y;
    sudo systemctl stop snmpd;
    sudo mv /etc/snmp/snmpd.conf /etc/snmp/snmpd.conf.orig;
    sudo cp python_tests/snmpd.conf /etc/snmp/snmpd.conf;
    sudo download-mibs;
    mkdir -p -m 0755 ~/.snmp;
    echo 'mibs +ALL' > ~/.snmp/snmp.conf;
    sudo systemctl start snmpd;
    rm -drf build/ ezsnmp.egg-info/ .tox/ .pytest_cache/ python_tests/__pycache__/ ezsnmp/__pycache__/ dist/;
    python3 -m pip install -r python_tests/requirements.txt;
    tox
    # Bottom one for debug. Replace the top one with it if needed.
    # python3 -m pip install . && gdb -ex run -ex bt -ex quit --args python3 -m pytest .;
    # Bottom one for valgrind. Replace the top one with it if needed.
    # python3 -m pip install . && valgrind --tool=memcheck --leak-check=full --show-leak-kinds=definite,indirect,possible python3 -m pytest .
    # Bottom one for valgrind using helgrind. Replace the top one with it if needed.
    # python3 -m pip install . && valgrind --tool=helgrind --free-is-write=yes python3 -m pytest .

C++ Tests
~~~~~~~~~

C++ tests use Google Test and Meson/Ninja build system. To run C++ tests:

.. code:: bash

    # Install prerequisites (on Ubuntu/Debian)
    sudo apt install -y meson ninja-build libgtest-dev lcov

    # Build and run C++ tests
    cd cpp_tests
    meson setup build
    ninja -C build
    meson test -C build --verbose

    # Generate coverage report
    ./get_test_coverage.sh

The C++ tests include a compatibility macro ``EZSNMP_SKIP_TEST_AND_RETURN_IF_NO_DATA`` that works with both older and newer versions of Google Test. This macro gracefully skips tests when SNMP data is unavailable.

For more details on C++ tests, see the `C++ Tests README <../../cpp_tests/README.rst>`_.


Running Tests with Docker
--------------------------

EzSnmp provides pre-built Docker images for testing across multiple Linux distributions. This ensures consistent testing environments. The project supports the following distributions:

* **almalinux10** - AlmaLinux 10 Kitten with Python 3.10-3.14, g++ 14.x
* **archlinux** - Arch Linux with Python 3.10-3.14, g++ 14.x
* **archlinux_netsnmp_5.8** - Arch Linux with net-snmp 5.8 for compatibility testing
* **centos7** - CentOS 7 with devtoolset-11 (g++ 11.2.1), Python 3.10-3.14
* **rockylinux8** - Rocky Linux 8 with gcc-toolset-11 (g++ 11.3.1), Python 3.10-3.14

Docker Python Tests
~~~~~~~~~~~~~~~~~~~

To run Python tests in Docker:

.. code:: bash

    # Run all Python tests across all distributions (parallel)
    cd docker/
    chmod +x run_python_tests_in_all_dockers.sh
    ./run_python_tests_in_all_dockers.sh

    # Run tests in a specific distribution only
    ./run_python_tests_in_all_dockers.sh almalinux10

    # Run a specific distribution image manually for Python tests
    sudo docker pull carlkidcrypto/ezsnmp_test_images:almalinux10-latest
    sudo docker run -d \
      --name "almalinux10_snmp_container" \
      -v "$(pwd):/ezsnmp" \
      carlkidcrypto/ezsnmp_test_images:almalinux10-latest \
      /bin/bash -c "/ezsnmp/docker/almalinux10/DockerEntry.sh false & tail -f /dev/null"

    # Execute Python tests inside the container using tox
    sudo docker exec -t almalinux10_snmp_container bash -c '
      export PATH=/usr/local/bin:/opt/rh/gcc-toolset-11/root/usr/bin:/opt/rh/devtoolset-11/root/usr/bin:$PATH;
      export LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib64:$LD_LIBRARY_PATH;
      export WORK_DIR=/tmp/ezsnmp_test;
      export TOX_WORK_DIR=/tmp/tox_test;
      rm -rf $WORK_DIR $TOX_WORK_DIR;
      mkdir -p $WORK_DIR;
      cd /ezsnmp && tar --exclude="*.egg-info" --exclude="build" --exclude="dist" --exclude=".tox" --exclude="__pycache__" --exclude="*.pyc" --exclude=".coverage*" --exclude="python3.*venv" --exclude="*.venv" --exclude="venv" -cf - . 2>/dev/null | (cd $WORK_DIR && tar xf -);
      cd $WORK_DIR;
      python3 -m pip install tox > /dev/null 2>&1;
      tox --workdir $TOX_WORK_DIR;
    '

Docker C++ Tests
~~~~~~~~~~~~~~~~

To run C++ tests in Docker:

.. code:: bash

    # Run C++ tests across all distributions
    cd docker/
    chmod +x run_cpp_tests_in_all_dockers.sh
    ./run_cpp_tests_in_all_dockers.sh

    # Run C++ tests in a specific distribution
    ./run_cpp_tests_in_all_dockers.sh rockylinux8

For more information on Docker testing, see the `Docker README <../../docker/README.rst>`_.


Python Tests on MacOS
~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    git clone https://github.com/carlkidcrypto/ezsnmp.git;
    cd ezsnmp;
    sudo mv /etc/snmp/snmpd.conf /etc/snmp/snmpd.conf.orig;
    sudo cp python_tests/snmpd.conf /etc/snmp/snmpd.conf;
    sudo launchctl unload /System/Library/LaunchDaemons/org.net-snmp.snmpd.plist;
    sudo launchctl load -w /System/Library/LaunchDaemons/org.net-snmp.snmpd.plist;
    rm -drf build/ ezsnmp.egg-info/ .tox/ .pytest_cache/ python_tests/__pycache__/ ezsnmp/__pycache__/ dist/;
    python3 -m pip install -r python_tests/requirements.txt;
    tox


Note: If you have issues installing the python package without HomeBrew or Ports try to update your Xcode Command Line Tools:
.. code:: bash

    # List available software updates
    softwareupdate --list

    # Example output:
    # Software Update found the following new or updated software:
    # * Label: Command Line Tools for Xcode-16.4
    #         Title: Command Line Tools for Xcode, Version: 16.4, Size: 861558KiB, Recommended: YES

    # Install the Command Line Tools for Xcode (use quotes around the label)
    softwareupdate -i "Command Line Tools for Xcode-16.4"

Running cibuildwheels
---------------------

For Linux builds on a Linux machine

.. code:: bash

    clear && rm -drf wheelhouse/ build/ ezsnmp.egg-info/  && python3 -m cibuildwheel --output-dir wheelhouse --platform linux


For MacOS builds on a MacOS machine

.. code:: bash

    clear && rm -drf wheelhouse/ build/ ezsnmp.egg-info/  && python3 -m cibuildwheel --output-dir wheelhouse --platform macos


Formatting
----------

For c++ code using clang-format 20+:

.. code:: bash

    find . -iname '*.h' -o -iname '*.cpp' | xargs clang-format-20 -i --style=file:.clang-format

For python3 code:

.. code:: bash

    python3 -m black .

Generating The CHANGELOG.md
---------------------------
To generate the changelog, run the following command:

.. code:: bash

    sudo snap install go --classic
    go install github.com/git-chglog/git-chglog/cmd/git-chglog@latest
    rm -rf CHANGELOG.md
    ~/go/bin/git-chglog --config .chglog/config.yml -o CHANGELOG.md
    git add CHANGELOG.md
    git commit -m "Updated CHANGELOG.md"