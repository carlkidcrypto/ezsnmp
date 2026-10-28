project('ezsnmp_tests', 'cpp', version: '2026.10.18a0', default_options: ['cpp_std=c++17', 'b_coverage=true'])

# Find required dependencies
gtest_dep = dependency('gtest', main: true)
thread_dep = dependency('threads')
# Net-SNMP supplies the OpenSSL ABI it was built against. Linking a separate
# OpenSSL dependency here mixes incompatible libcrypto versions in legacy
# compatibility containers (for example OpenSSL 1.0 with OpenSSL 3).
openssl_dep = declare_dependency()
if host_machine.system() == 'darwin'
    # Homebrew keeps OpenSSL keg-only, while its net-snmp pkg-config metadata
    # omits the OpenSSL include directory required by public Net-SNMP headers.
    openssl_dep = dependency('openssl', required: true)
endif

# MACOS with homebrew needs this: export PKG_CONFIG_PATH="/opt/homebrew/opt/net-snmp/lib/pkgconfig:$PKG_CONFIG_PATH"
# Find the netsnmp dependency and make it required for the build to proceed.
netsnmp_dep = dependency('netsnmp', required: true)

# Net-SNMP sources directory (uses net-snmp-5.10-final-patched for Net-SNMP 5.10+)
netsnmp_version = netsnmp_dep.version()
snmp_source_dir = '../ezsnmp/src/net-snmp-5.10-final-patched'

message('Using Net-SNMP sources from: @0@'.format(snmp_source_dir))

# Include parent directory for ezsnmp headers
include_dirs = include_directories('..', '../ezsnmp/include')
common_deps = [gtest_dep, thread_dep, netsnmp_dep, openssl_dep]

# Shared library source paths
datatypes_src = join_paths(snmp_source_dir, '../datatypes.cpp')
exceptionsbase_src = join_paths(snmp_source_dir, '../exceptionsbase.cpp')
helpers_src = join_paths(snmp_source_dir, '../helpers.cpp')
thread_safety_src = join_paths(snmp_source_dir, '../thread_safety.cpp')
sessionbase_src = join_paths(snmp_source_dir, '../sessionbase.cpp')
snmpbulkget_src = join_paths(snmp_source_dir, 'snmpbulkget.cpp')
snmpbulkwalk_src = join_paths(snmp_source_dir, 'snmpbulkwalk.cpp')
snmpget_src = join_paths(snmp_source_dir, 'snmpget.cpp')
snmpgetnext_src = join_paths(snmp_source_dir, 'snmpgetnext.cpp')
snmpset_src = join_paths(snmp_source_dir, 'snmpset.cpp')
snmptrap_src = join_paths(snmp_source_dir, 'snmptrap.cpp')
snmpwalk_src = join_paths(snmp_source_dir, 'snmpwalk.cpp')

common_shim_sources = [
    helpers_src,
    datatypes_src,
    thread_safety_src,
    exceptionsbase_src,
]

sessionbase_all_sources = [
    sessionbase_src,
    exceptionsbase_src,
    helpers_src,
    thread_safety_src,
    snmpbulkget_src,
    snmpbulkwalk_src,
    snmpget_src,
    snmpgetnext_src,
    snmpset_src,
    snmpwalk_src,
    datatypes_src,
]

# Compile each core ezsnmp C++ source once and extract exact object subsets per test
# executable instead of recompiling shared sources 60+ times across 65 binaries.
ezsnmp_shared_objs = static_library(
    'ezsnmp_shared_objs',
    [
        datatypes_src,
        exceptionsbase_src,
        helpers_src,
        thread_safety_src,
        sessionbase_src,
        snmpbulkget_src,
        snmpbulkwalk_src,
        snmpget_src,
        snmpgetnext_src,
        snmpset_src,
        snmptrap_src,
        snmpwalk_src,
    ],
    include_directories: include_dirs,
    dependencies: [thread_dep, netsnmp_dep, openssl_dep],
    build_by_default: false,
)

# Create test executables
test_datatypes = executable(
    'test_datatypes',
    ['test_datatypes.cpp'],
    objects: ezsnmp_shared_objs.extract_objects(datatypes_src),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_helpers = executable(
    'test_helpers',
    ['test_helpers.cpp'],
    objects: ezsnmp_shared_objs.extract_objects(common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_thread_safety = executable(
    'test_thread_safety',
    ['test_thread_safety.cpp'],
    objects: ezsnmp_shared_objs.extract_objects(thread_safety_src),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_sessionbase = executable(
    'test_sessionbase',
    ['test_sessionbase.cpp'],
    objects: ezsnmp_shared_objs.extract_objects(sessionbase_all_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_sessionbase_parameters = executable(
    'test_sessionbase_parameters',
    ['test_sessionbase_parameters.cpp'],
    objects: ezsnmp_shared_objs.extract_objects(sessionbase_all_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_sessionbase_v3_guard_shim = executable(
    'test_sessionbase_v3_guard_shim',
    ['test_sessionbase_v3_guard_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects(
        sessionbase_src,
        exceptionsbase_src,
        thread_safety_src,
    ),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpget = executable(
    'test_snmpget',
    ['test_snmpget.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpget_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpget_shim = executable(
    'test_snmpget_shim',
    ['test_snmpget_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpget_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpgetnext = executable(
    'test_snmpgetnext',
    ['test_snmpgetnext.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpgetnext_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpgetnext_shim = executable(
    'test_snmpgetnext_shim',
    ['test_snmpgetnext_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpgetnext_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpset = executable(
    'test_snmpset',
    ['test_snmpset.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpset_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmptrap = executable(
    'test_snmptrap',
    ['test_snmptrap.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmptrap_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpwalk = executable(
    'test_snmpwalk',
    ['test_snmpwalk.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpwalk_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpwalk_shim = executable(
    'test_snmpwalk_shim',
    ['test_snmpwalk_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpwalk_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpbulkget = executable(
    'test_snmpbulkget',
    ['test_snmpbulkget.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpbulkget_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpbulkget_shim = executable(
    'test_snmpbulkget_shim',
    ['test_snmpbulkget_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpbulkget_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpbulkwalk = executable(
    'test_snmpbulkwalk',
    ['test_snmpbulkwalk.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpbulkwalk_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_exceptionsbase = executable(
    'test_exceptionsbase',
    ['test_exceptionsbase.cpp'],
    objects: ezsnmp_shared_objs.extract_objects(exceptionsbase_src),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_helpers_session_perror_shim = executable(
    'test_helpers_session_perror_shim',
    ['test_helpers_session_perror_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects(common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_helpers_branches_shim = executable(
    'test_helpers_branches_shim',
    ['test_helpers_branches_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects(common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_helpers_single_sess_perror_shim = executable(
    'test_helpers_single_sess_perror_shim',
    ['test_helpers_single_sess_perror_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects(common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_helpers_snmp_perror_shim = executable(
    'test_helpers_snmp_perror_shim',
    ['test_helpers_snmp_perror_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects(common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_helpers_connection_error_variants_shim = executable(
    'test_helpers_connection_error_variants_shim',
    ['test_helpers_connection_error_variants_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects(common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpget_null_shim = executable(
    'test_snmpget_null_shim',
    ['test_snmpget_null_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpget_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpgetnext_null_shim = executable(
    'test_snmpgetnext_null_shim',
    ['test_snmpgetnext_null_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpgetnext_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpset_null_shim = executable(
    'test_snmpset_null_shim',
    ['test_snmpset_null_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpset_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpbulkget_null_shim = executable(
    'test_snmpbulkget_null_shim',
    ['test_snmpbulkget_null_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpbulkget_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpwalk_null_shim = executable(
    'test_snmpwalk_null_shim',
    ['test_snmpwalk_null_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpwalk_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpbulkwalk_shim = executable(
    'test_snmpbulkwalk_shim',
    ['test_snmpbulkwalk_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpbulkwalk_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

test_snmpbulkwalk_null_shim = executable(
    'test_snmpbulkwalk_null_shim',
    ['test_snmpbulkwalk_null_shim.cpp'],
    objects: ezsnmp_shared_objs.extract_objects([snmpbulkwalk_src] + common_shim_sources),
    include_directories: include_dirs,
    dependencies: common_deps
)

# ----- New shim executables for coverage improvement -----

new_shim_tests_map = {
    'snmpwalk': ['_timeout', '_nosuchname', '_get_and_print', '_with_data', '_parse_args', '_stat_error', '_order'],
    'snmpbulkwalk': ['_timeout', '_nosuchname', '_get_and_print', '_with_data', '_parse_args', '_stat_error', '_order'],
    'snmpbulkget': ['_nosuchname', '_timeout', '_parse_args', '_stat_error'],
    'snmpget': ['_timeout', '_parse_args', '_stat_error', '_errindex'],
    'snmpgetnext': ['_timeout', '_parse_args', '_stat_error', '_errindex'],
    'snmpset': ['', '_timeout', '_parse_args', '_stat_error', '_addvar'],
    'snmptrap': ['_parse_args', '_null', '_stat_error', '_v1_branch'],
}

new_shim_executables = {}
foreach op, suffixes : new_shim_tests_map
    op_source = join_paths(snmp_source_dir, op + '.cpp')
    foreach suffix : suffixes
        test_name = 'test_' + op + suffix + '_shim'
        exe = executable(
            test_name,
            [test_name + '.cpp'],
            objects: ezsnmp_shared_objs.extract_objects([op_source] + common_shim_sources),
            include_directories: include_dirs,
            dependencies: common_deps
        )
        new_shim_executables += {test_name: exe}
    endforeach
endforeach

# Register tests
test_env = environment()

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
test('sessionbase_v3_guard_shim_test', test_sessionbase_v3_guard_shim, env: test_env)
test('snmpget_test', test_snmpget, env: test_env)
test('snmpget_shim_test', test_snmpget_shim, env: test_env)
test('snmpget_null_shim_test', test_snmpget_null_shim, env: test_env)
test('snmpgetnext_test', test_snmpgetnext, env: test_env)
test('snmpgetnext_shim_test', test_snmpgetnext_shim, env: test_env)
test('snmpgetnext_null_shim_test', test_snmpgetnext_null_shim, env: test_env)
test('snmpset_test', test_snmpset, env: test_env)
test('snmpset_null_shim_test', test_snmpset_null_shim, env: test_env)
test('snmptrap_test', test_snmptrap, env: test_env)
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
test('helpers_snmp_perror_shim_test', test_helpers_snmp_perror_shim, env: test_env)
test('helpers_connection_error_variants_shim_test', test_helpers_connection_error_variants_shim, env: test_env)

# New shim tests for coverage improvement
foreach test_name, exe : new_shim_executables
    test(test_name + '_test', exe, env: test_env)
endforeach
