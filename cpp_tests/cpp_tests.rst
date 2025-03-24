Installing and Running Tests with Google Test
=============================================

This guide explains how to set up Google Test, Meson, and Ninja for building and running tests on Linux.

Installing Google Test
----------------------

1. Install required packages::

    sudo apt-get update &&
    sudo apt-get install libgtest-dev

Installing Meson and Ninja
--------------------------

1. Install Meson and Ninja using apt::

    sudo apt-get update &&
    sudo apt-get install meson ninja-build

Installing Dependencies
-----------------------

1. Install the required dependencies for the tests::

    sudo apt-get install libsnmp-dev pkg-config lcov

Building and Running Tests
--------------------------

1. Initialize build directory::

    cd cpp_tests &&
    meson setup build/

2. Build the tests::

    ninja -C build/

3. Run the tests::

    ninja -C build/ test

Or alternatively::

    meson test

The test results will be displayed in the terminal. For detailed output, use::

    meson test -v

Running Specific Tests and Coverage
----------------------------------

1. To run a specific test suite::

    clear && ninja -C build/ && ./build/test_sessionbase

2. To run all test suites::

    clear && ninja -C build/ test


Coverage Reports
----------------

1. To generate coverage reports, run the following commands::

    clear && ./get_test_coverage.sh 
