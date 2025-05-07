Development Guide
=================

How to Generate the Sphinx Documentation
----------------------------------------

You may generate the documentation as follows:

.. code:: bash

    # Install Sphinx
    # See this website for install instructions https://www.sphinx-doc.org/en/master/usage/installation.html

    # Build the documentation into static HTML pages
    cd sphinx_docs_build
    python3 -m pip install -r requirements.txt
    make html

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

Tests use `Pytest <https://github.com/pytest-dev/pytest>`_. You can run
them with the following on Linux:

.. code:: bash

    git clone https://github.com/ezsnmp/ezsnmp.git;
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
    rm -drf build/ dist/ ezsnmp.egg-info;
    python3 -m pip install -r python_tests/requirements.txt;
    python3 -m pip install . && pytest python_tests/;
    # Bottom one for debug. Replace the top one with it if needed.
    # python3 -m pip install . && gdb -ex run -ex bt -ex quit --args python3 -m pytest .;
    # Bottom one for valgrind. Replace the top one with it if needed.
    # python3 -m pip install . && valgrind --tool=memcheck --leak-check=full --show-leak-kinds=definite,indirect,possible python3 -m pytest .
    # Bottom one for valgrind using helgrind. Replace the top one with it if needed.
    # python3 -m pip install . && valgrind --tool=helgrind --free-is-write=yes python3 -m pytest .


On MacOS

.. code:: bash

    git clone https://github.com/ezsnmp/ezsnmp.git;
    cd ezsnmp;
    sudo mv /etc/snmp/snmpd.conf /etc/snmp/snmpd.conf.orig;
    sudo cp python_tests/snmpd.conf /etc/snmp/snmpd.conf;
    sudo launchctl unload /System/Library/LaunchDaemons/org.net-snmp.snmpd.plist;
    sudo launchctl load -w /System/Library/LaunchDaemons/org.net-snmp.snmpd.plist;
    rm -drf build/ dist/ ezsnmp.egg-info;
    python3 -m pip install -r python_tests/requirements.txt;
    python3 -m pip install . && pytest python_tests/;


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

    find . -iname '*.h' -o -iname '*.cpp' | xargs clang-format -i --style=file:.clang-format

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