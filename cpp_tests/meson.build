project('ezsnmp_tests',  'cpp', default_options: ['cpp_std=c++17'])

# This no worky on mac
# add_project_arguments('-fprofile-arcs', '-ftest-coverage', language: 'cpp')
# add_project_link_arguments('-lgcov', language: 'cpp')

# Find required dependencies
gtest_dep = dependency('gtest', main: true)
thread_dep = dependency('threads')

# MACOS with homebrew needs this: export PKG_CONFIG_PATH="/opt/homebrew/opt/net-snmp/lib/pkgconfig:$PKG_CONFIG_PATH"
# Find the netsnmp dependency and make it required for the build to proceed.
netsnmp_dep = dependency('netsnmp', required: true)

# Conditionally select source directory based on the net-snmp version.
netsnmp_version = netsnmp_dep.version()
snmp_source_dir = '' 

if netsnmp_version.endswith('5.9')
  snmp_source_dir = '../ezsnmp/src/net-snmp-5.9-final-patched'
elif netsnmp_version.endswith('5.8')
  snmp_source_dir = '../ezsnmp/src/net-snmp-5.8-final-patched'
elif netsnmp_version.endswith('5.7')
  snmp_source_dir = '../ezsnmp/src/net-snmp-5.7-final-patched'
elif netsnmp_version.endswith('5.6')
  snmp_source_dir = '../ezsnmp/src/net-snmp-5.6-final-patched'
else
  # Fallback for any other version (e.g., newer or unhandled older versions)
  snmp_source_dir = '../ezsnmp/src'
endif

message('Using Net-SNMP sources from: @0@'.format(snmp_source_dir))

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