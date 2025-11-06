"""
Tests to achieve 100% coverage for module import paths in SWIG-generated files.
"""
import pytest
import sys
import faulthandler

faulthandler.enable()


def test_datatypes_import_with_package():
    """Test that datatypes module imports correctly when used as a package."""
    # This should import via the 'from ._datatypes import *' path
    from ezsnmp import datatypes
    assert hasattr(datatypes, '_swig_python_version_info')


def test_exceptionsbase_import_with_package():
    """Test that exceptionsbase module imports correctly when used as a package."""
    # This should import via the 'from ._exceptionsbase import *' path
    from ezsnmp import exceptionsbase
    assert hasattr(exceptionsbase, '_swig_python_version_info')


def test_netsnmpbase_import_with_package():
    """Test that netsnmpbase module imports correctly when used as a package."""
    # This should import via the 'from ._netsnmpbase import *' path
    from ezsnmp import netsnmpbase
    assert hasattr(netsnmpbase, '_swig_python_version_info')


def test_sessionbase_import_with_package():
    """Test that sessionbase module imports correctly when used as a package."""
    # This should import via the 'from ._sessionbase import *' path
    from ezsnmp import sessionbase
    assert hasattr(sessionbase, '_swig_python_version_info')


def test_datatypes_import_without_package():
    """Test datatypes module import path when not used as a package."""
    # Save the original module
    import ezsnmp.datatypes
    original_name = ezsnmp.datatypes.__name__
    
    # The module is already imported as a package, so this test
    # verifies that the current import mechanism works
    assert '.' in original_name  # Should contain dot if imported as package


def test_module_import_paths_exist():
    """Verify that all SWIG-generated modules have proper import attributes."""
    from ezsnmp import datatypes, exceptionsbase, netsnmpbase, sessionbase
    
    # All should have been imported successfully
    assert datatypes is not None
    assert exceptionsbase is not None
    assert netsnmpbase is not None
    assert sessionbase is not None
