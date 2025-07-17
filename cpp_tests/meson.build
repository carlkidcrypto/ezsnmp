project('ezsnmp_tests',  'cpp', default_options: ['cpp_std=c++17'])

# This no worky on mac
# add_project_arguments('-fprofile-arcs', '-ftest-coverage', language: 'cpp')
# add_project_link_arguments('-lgcov', language: 'cpp')

# Find required dependencies
gtest_dep = dependency('gtest', main: true)
thread_dep = dependency('threads')

# MACOS with homebrew needs this: export PKG_CONFIG_PATH="/opt/homebrew/opt/net-snmp/lib/pkgconfig:$PKG_CONFIG_PATH"
netsnmp_dep = dependency('netsnmp')

# Include parent directory for ezsnmp headers
include_dirs = include_directories('..', '../ezsnmp/include')

# Create test executables
test_datatypes = executable(
    'test_datatypes',
    [
        'test_datatypes.cpp',
        '../ezsnmp/src/datatypes.cpp',
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep]
)

test_helpers = executable(
    'test_helpers',
    [
        'test_helpers.cpp',
        '../ezsnmp/src/helpers.cpp',
        '../ezsnmp/src/exceptionsbase.cpp',
        '../ezsnmp/src/datatypes.cpp',
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep]
)

test_sessionbase = executable(
    'test_sessionbase',
    [
        'test_sessionbase.cpp',
        '../ezsnmp/src/sessionbase.cpp',
        '../ezsnmp/src/exceptionsbase.cpp',
        '../ezsnmp/src/helpers.cpp',
        '../ezsnmp/src/snmpbulkget.cpp',
        '../ezsnmp/src/snmpbulkwalk.cpp',
        '../ezsnmp/src/snmpget.cpp',
        '../ezsnmp/src/snmpgetnext.cpp',
        '../ezsnmp/src/snmpset.cpp',
        '../ezsnmp/src/snmpwalk.cpp',
        '../ezsnmp/src/datatypes.cpp',
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep]
)

test_snmpget = executable(
    'test_snmpget',
    [
        'test_snmpget.cpp',
        '../ezsnmp/src/snmpget.cpp',
        '../ezsnmp/src/helpers.cpp',
        '../ezsnmp/src/datatypes.cpp',
        '../ezsnmp/src/exceptionsbase.cpp',
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep]
)

# Register tests
test('datatypes_test', test_datatypes)
test('helpers_test', test_helpers)
test('sessionbase_test', test_sessionbase)
test('snmpget_test', test_snmpget)