project('ezsnmp_tests', 'cpp', version: '2.0.0', default_options: ['cpp_std=c++17', 'b_coverage=true'])

# Enable coverage on Linux only
if host_machine.system() == 'linux'
  add_project_arguments(['-fprofile-arcs', '-ftest-coverage', '--coverage'], language: 'cpp')
  add_project_link_arguments(['--coverage'], language: 'cpp')
endif

# Find required dependencies
gtest_dep = dependency('gtest', main: true)
thread_dep = dependency('threads')
openssl_dep = dependency('openssl', required: true)

# MACOS with homebrew needs this: export PKG_CONFIG_PATH="/opt/homebrew/opt/net-snmp/lib/pkgconfig:$PKG_CONFIG_PATH"
# Find the netsnmp dependency and make it required for the build to proceed.
netsnmp_dep = dependency('netsnmp', required: true)

# Conditionally select source directory based on the net-snmp version.
netsnmp_version = netsnmp_dep.version()
snmp_source_dir = '' 

if netsnmp_version.startswith('5.9')
  snmp_source_dir = '../ezsnmp/src/net-snmp-5.9-final-patched'
elif netsnmp_version.startswith('5.8')
  snmp_source_dir = '../ezsnmp/src/net-snmp-5.8-final-patched'
elif netsnmp_version.startswith('5.7')
  snmp_source_dir = '../ezsnmp/src/net-snmp-5.7-final-patched'
elif netsnmp_version.startswith('5.6')
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
        join_paths(snmp_source_dir, '../datatypes.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_helpers = executable(
    'test_helpers',
    [
        'test_helpers.cpp',
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_sessionbase = executable(
    'test_sessionbase',
    [
        'test_sessionbase.cpp',
        join_paths(snmp_source_dir, '../sessionbase.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, 'snmpbulkget.cpp'),
        join_paths(snmp_source_dir, 'snmpbulkwalk.cpp'),
        join_paths(snmp_source_dir, 'snmpget.cpp'),
        join_paths(snmp_source_dir, 'snmpgetnext.cpp'),
        join_paths(snmp_source_dir, 'snmpset.cpp'),
        join_paths(snmp_source_dir, 'snmpwalk.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_sessionbase_parameters = executable(
    'test_sessionbase_parameters',
    [
        'test_sessionbase_parameters.cpp',
        join_paths(snmp_source_dir, '../sessionbase.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, 'snmpbulkget.cpp'),
        join_paths(snmp_source_dir, 'snmpbulkwalk.cpp'),
        join_paths(snmp_source_dir, 'snmpget.cpp'),
        join_paths(snmp_source_dir, 'snmpgetnext.cpp'),
        join_paths(snmp_source_dir, 'snmpset.cpp'),
        join_paths(snmp_source_dir, 'snmpwalk.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpget = executable(
    'test_snmpget',
    [
        'test_snmpget.cpp',
        join_paths(snmp_source_dir, 'snmpget.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpgetnext = executable(
    'test_snmpgetnext',
    [
        'test_snmpgetnext.cpp',
        join_paths(snmp_source_dir, 'snmpgetnext.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpset = executable(
    'test_snmpset',
    [
        'test_snmpset.cpp',
        join_paths(snmp_source_dir, 'snmpset.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpwalk = executable(
    'test_snmpwalk',
    [
        'test_snmpwalk.cpp',
        join_paths(snmp_source_dir, 'snmpwalk.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpbulkget = executable(
    'test_snmpbulkget',
    [
        'test_snmpbulkget.cpp',
        join_paths(snmp_source_dir, 'snmpbulkget.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpbulkwalk = executable(
    'test_snmpbulkwalk',
    [
        'test_snmpbulkwalk.cpp',
        join_paths(snmp_source_dir, 'snmpbulkwalk.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_exceptionsbase = executable(
    'test_exceptionsbase',
    [
        'test_exceptionsbase.cpp',
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

# Register tests
test('datatypes_test', test_datatypes)
test('helpers_test', test_helpers)
test('sessionbase_test', test_sessionbase)
test('sessionbase_parameters_test', test_sessionbase_parameters)
test('snmpget_test', test_snmpget)
test('snmpgetnext_test', test_snmpgetnext)
test('snmpset_test', test_snmpset)
test('snmpwalk_test', test_snmpwalk)
test('snmpbulkget_test', test_snmpbulkget)
test('snmpbulkwalk_test', test_snmpbulkwalk)
test('exceptionsbase_test', test_exceptionsbase)