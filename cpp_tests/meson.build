project('ezsnmp_tests', 'cpp', version: '2.3.0a1', default_options: ['cpp_std=c++17', 'b_coverage=true'])

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
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_thread_safety = executable(
    'test_thread_safety',
    [
        'test_thread_safety.cpp',
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
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
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
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
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
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
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpget_shim = executable(
    'test_snmpget_shim',
    [
        'test_snmpget_shim.cpp',
        join_paths(snmp_source_dir, 'snmpget.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
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
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpgetnext_shim = executable(
    'test_snmpgetnext_shim',
    [
        'test_snmpgetnext_shim.cpp',
        join_paths(snmp_source_dir, 'snmpgetnext.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
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
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
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
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpwalk_shim = executable(
    'test_snmpwalk_shim',
    [
        'test_snmpwalk_shim.cpp',
        join_paths(snmp_source_dir, 'snmpwalk.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
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
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpbulkget_shim = executable(
    'test_snmpbulkget_shim',
    [
        'test_snmpbulkget_shim.cpp',
        join_paths(snmp_source_dir, 'snmpbulkget.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
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
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
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

test_helpers_session_perror_shim = executable(
    'test_helpers_session_perror_shim',
    [
        'test_helpers_session_perror_shim.cpp',
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_helpers_branches_shim = executable(
    'test_helpers_branches_shim',
    [
        'test_helpers_branches_shim.cpp',
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_helpers_single_sess_perror_shim = executable(
    'test_helpers_single_sess_perror_shim',
    [
        'test_helpers_single_sess_perror_shim.cpp',
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpget_null_shim = executable(
    'test_snmpget_null_shim',
    [
        'test_snmpget_null_shim.cpp',
        join_paths(snmp_source_dir, 'snmpget.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpgetnext_null_shim = executable(
    'test_snmpgetnext_null_shim',
    [
        'test_snmpgetnext_null_shim.cpp',
        join_paths(snmp_source_dir, 'snmpgetnext.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpset_null_shim = executable(
    'test_snmpset_null_shim',
    [
        'test_snmpset_null_shim.cpp',
        join_paths(snmp_source_dir, 'snmpset.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpbulkget_null_shim = executable(
    'test_snmpbulkget_null_shim',
    [
        'test_snmpbulkget_null_shim.cpp',
        join_paths(snmp_source_dir, 'snmpbulkget.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpwalk_null_shim = executable(
    'test_snmpwalk_null_shim',
    [
        'test_snmpwalk_null_shim.cpp',
        join_paths(snmp_source_dir, 'snmpwalk.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpbulkwalk_shim = executable(
    'test_snmpbulkwalk_shim',
    [
        'test_snmpbulkwalk_shim.cpp',
        join_paths(snmp_source_dir, 'snmpbulkwalk.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

test_snmpbulkwalk_null_shim = executable(
    'test_snmpbulkwalk_null_shim',
    [
        'test_snmpbulkwalk_null_shim.cpp',
        join_paths(snmp_source_dir, 'snmpbulkwalk.cpp'),
        join_paths(snmp_source_dir, '../helpers.cpp'),
        join_paths(snmp_source_dir, '../datatypes.cpp'),
        join_paths(snmp_source_dir, '../thread_safety.cpp'),
        join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
)

# ----- New shim executables for coverage improvement -----

common_shim_sources = [
    join_paths(snmp_source_dir, '../helpers.cpp'),
    join_paths(snmp_source_dir, '../datatypes.cpp'),
    join_paths(snmp_source_dir, '../thread_safety.cpp'),
    join_paths(snmp_source_dir, '../exceptionsbase.cpp'),
]

new_shim_tests_map = {
    'snmpwalk': ['_timeout', '_nosuchname', '_get_and_print', '_with_data', '_parse_args', '_stat_error', '_order'],
    'snmpbulkwalk': ['_timeout', '_nosuchname', '_get_and_print', '_with_data', '_parse_args', '_stat_error', '_order'],
    'snmpbulkget': ['_nosuchname', '_timeout', '_parse_args', '_stat_error'],
    'snmpget': ['_timeout', '_parse_args', '_stat_error', '_errindex'],
    'snmpgetnext': ['_timeout', '_parse_args', '_stat_error', '_errindex'],
    'snmpset': ['', '_timeout', '_parse_args', '_stat_error', '_addvar'],
}

new_shim_executables = {}
foreach op, suffixes : new_shim_tests_map
    op_source = join_paths(snmp_source_dir, op + '.cpp')
    foreach suffix : suffixes
        test_name = 'test_' + op + suffix + '_shim'
        test_sources = [test_name + '.cpp', op_source] + common_shim_sources
        exe = executable(
            test_name,
            test_sources,
            include_directories: include_dirs,
            dependencies: [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]
        )
        new_shim_executables += {test_name: exe}
    endforeach
endforeach

# Register tests
# For net-snmp 5.7, disable malloc perturbation to avoid false positives
# with glibc's strict malloc checking (incompatible with net-snmp 5.7's memory patterns)
test_env = environment()
if netsnmp_version.startswith('5.7')
  test_env.set('MALLOC_PERTURB_', '0')
  test_env.set('MALLOC_CHECK_', '0')
endif

# Ensure SNMP MIBs are loaded during tests so that symbolic OID names
# (e.g. SNMPv2-MIB::sysORDescr) resolve correctly on all platforms.
test_env.set('MIBS', 'ALL')
mibdirs_cmd = run_command('net-snmp-config', '--default-mibdirs', check: false)
if mibdirs_cmd.returncode() == 0 and mibdirs_cmd.stdout().strip() != ''
  test_env.set('MIBDIRS', mibdirs_cmd.stdout().strip())
else
  test_env.set('MIBDIRS', '/usr/share/snmp/mibs:/usr/share/snmp/mibs/iana:/usr/share/snmp/mibs/ietf')
endif

test('datatypes_test', test_datatypes, env: test_env)
test('helpers_test', test_helpers, env: test_env)
test('thread_safety_test', test_thread_safety, env: test_env)
test('sessionbase_test', test_sessionbase, env: test_env)
test('sessionbase_parameters_test', test_sessionbase_parameters, env: test_env)
test('snmpget_test', test_snmpget, env: test_env)
test('snmpget_shim_test', test_snmpget_shim, env: test_env)
test('snmpget_null_shim_test', test_snmpget_null_shim, env: test_env)
test('snmpgetnext_test', test_snmpgetnext, env: test_env)
test('snmpgetnext_shim_test', test_snmpgetnext_shim, env: test_env)
test('snmpgetnext_null_shim_test', test_snmpgetnext_null_shim, env: test_env)
test('snmpset_test', test_snmpset, env: test_env)
test('snmpset_null_shim_test', test_snmpset_null_shim, env: test_env)
test('snmpwalk_test', test_snmpwalk, env: test_env, timeout: 120)
test('snmpwalk_shim_test', test_snmpwalk_shim, env: test_env)
test('snmpwalk_null_shim_test', test_snmpwalk_null_shim, env: test_env)
test('snmpbulkget_test', test_snmpbulkget, env: test_env)
test('snmpbulkget_shim_test', test_snmpbulkget_shim, env: test_env)
test('snmpbulkget_null_shim_test', test_snmpbulkget_null_shim, env: test_env)
test('snmpbulkwalk_test', test_snmpbulkwalk, env: test_env)
test('snmpbulkwalk_shim_test', test_snmpbulkwalk_shim, env: test_env)
test('snmpbulkwalk_null_shim_test', test_snmpbulkwalk_null_shim, env: test_env)
test('exceptionsbase_test', test_exceptionsbase, env: test_env)
test('helpers_session_perror_shim_test', test_helpers_session_perror_shim, env: test_env)
test('helpers_branches_shim_test', test_helpers_branches_shim, env: test_env)
test('helpers_single_sess_perror_shim_test', test_helpers_single_sess_perror_shim, env: test_env)

# New shim tests for coverage improvement
foreach test_name, exe : new_shim_executables
    test(test_name + '_test', exe, env: test_env)
endforeach
