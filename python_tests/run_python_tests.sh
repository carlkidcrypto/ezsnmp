#!/usr/bin/env bash
#
# Run ezsnmp python tests from outside the source tree to avoid the local
# ezsnmp/ package directory shadowing the installed C extension modules.
#
# Usage:
#   ./run_python_tests.sh [pytest args...]
#
# Examples:
#   ./run_python_tests.sh
#   ./run_python_tests.sh -k test_getters
#   ./run_python_tests.sh -x --tb=short
#
# The script automatically inherits the active virtualenv. If VIRTUAL_ENV
# is set when this script is invoked, the same environment is used to run
# the tests.

set -euo pipefail

TEST_DIR="$(cd "$(dirname "$0")" && pwd)"

# Preserve the caller's virtualenv (if any) so the user doesn't need to
# re-activate it.  We just need VIRTUAL_ENV and PATH to be correct.
if [ -n "${VIRTUAL_ENV:-}" ]; then
    echo "Using virtualenv: ${VIRTUAL_ENV}"
    export PATH="${VIRTUAL_ENV}/bin:${PATH}"
fi

# Change to $HOME so the local ezsnmp/ source directory is not on sys.path.
cd "$HOME"

# Verify ezsnmp is importable from the installed package, not the source tree.
if ! python3 -c "import ezsnmp" 2>/dev/null; then
    echo "Error: ezsnmp is not installed. Run 'pip install .' first." >&2
    exit 1
fi

# Run pytest, passing the absolute path to the test directory and forwarding
# any extra arguments the caller supplied.
exec python3 -m pytest "${TEST_DIR}" -v -s "$@"
