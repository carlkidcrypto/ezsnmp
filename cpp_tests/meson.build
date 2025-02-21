project('ezsnmp_tests', 'cpp')

# Find required dependencies
gtest_dep = dependency('gtest', main: true)
thread_dep = dependency('threads')
netsnmp_dep = dependency('netsnmp')  # Add this line

# Include parent directory for ezsnmp headers
include_dirs = include_directories('..', '../ezsnmp/include')

# Create test executables
test_datatypes = executable(
    'test_datatypes',
    [
        'test_datatypes.cpp',
        '../ezsnmp/src/datatypes.cpp'
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
        '../ezsnmp/src/snmpwalk.cpp'
    ],
    include_directories: include_dirs,
    dependencies: [gtest_dep, thread_dep, netsnmp_dep]
)

# Register tests
test('datatypes_test', test_datatypes)
test('sessionbase_test', test_sessionbase)