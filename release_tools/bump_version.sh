#!/usr/bin/env bash

set -euo pipefail

usage() {
    cat <<'EOF'
Usage: release_tools/bump_version.sh [OPTIONS] NEW_VERSION [OLD_VERSION]

Bump the current release version across tracked configuration, build, and documentation files.
If OLD_VERSION is omitted, it is read automatically from setup.cfg.

Options:
    -n, --dry-run    Preview files that would be modified without writing changes.
    -v, --verify     Run black formatting, sphinx doc build (-W), and tests after bumping.
    -h, --help       Show this help message.

Examples:
    release_tools/bump_version.sh 2.5.0b0
    release_tools/bump_version.sh --dry-run 2.5.0b0
    release_tools/bump_version.sh --verify 2026.10.18a0
EOF
}

dry_run=false
verify=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        -n|--dry-run)
            dry_run=true
            shift
            ;;
        -v|--verify)
            verify=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            printf 'Unknown option: %s\n' "$1" >&2
            usage >&2
            exit 2
            ;;
        *)
            break
            ;;
    esac
done

if [[ $# -lt 1 || $# -gt 2 ]]; then
    usage >&2
    exit 2
fi

new_version="${1#v}"  # Strip leading 'v' if present
repo_root=$(git rev-parse --show-toplevel)
cd "$repo_root"

# Validate new version format (supports both SemVer e.g. 2.5.0b0 and CalVer e.g. 2026.10.18a0)
if [[ ! "$new_version" =~ ^[0-9]+(\.[0-9]+){2}([.-]?[0-9A-Za-z.-]+)?$ ]]; then
    printf 'Error: Invalid version format "%s". Expected SemVer (e.g. 2.5.0b0) or CalVer (e.g. 2026.10.18a0).\n' "$new_version" >&2
    exit 2
fi

if [[ $# -eq 2 ]]; then
    old_version="${2#v}"
else
    if [[ ! -f "setup.cfg" ]]; then
        printf 'Error: setup.cfg not found in %s\n' "$repo_root" >&2
        exit 1
    fi
    old_version=$(sed -nE 's/^version[[:space:]]*=[[:space:]]*([^[:space:]]+).*$/\1/p' setup.cfg | head -n 1)
fi

old_version="${old_version#v}"

if [[ -z "$old_version" ]]; then
    printf 'Error: Could not determine current version from setup.cfg\n' >&2
    exit 1
fi

if [[ "$old_version" == "$new_version" ]]; then
    printf 'Current version is already %s. Nothing to bump.\n' "$old_version"
    exit 0
fi

# Exclude historical files, build caches, and release tools themselves
pathspecs=(
    ':(exclude)CHANGELOG.md'
    ':(exclude)Formula/ezsnmp.rb'
    ':(exclude)docs/**'
    ':(exclude)sphinx_docs_build/landing/**'
    ':(exclude)build/**'
    ':(exclude)*.venv/**'
    ':(exclude)release_tools/**'
    ':(exclude).github/workflows/*.lock.yml'
    ':(exclude).github/scripts/**'
)

files=()
while IFS= read -r line; do
    [[ -n "$line" ]] && files+=("$line")
done < <(git grep -Il -F -- "$old_version" -- . "${pathspecs[@]}" || true)

required_files=(
    setup.cfg
    cpp_tests/meson.build
    sphinx_docs_build/source/conf.py
)

for required_file in "${required_files[@]}"; do
    if [[ ! " ${files[*]} " == *" $required_file "* ]]; then
        printf 'Error: Expected version "%s" not found in required file: %s\n' "$old_version" "$required_file" >&2
        exit 1
    fi
done

if [[ ${#files[@]} -eq 0 ]]; then
    printf 'Error: No tracked files contain version "%s"\n' "$old_version" >&2
    exit 1
fi

printf '%s version %s -> %s in %d file(s):\n' \
    "$([[ "$dry_run" == true ]] && printf 'Would bump' || printf 'Bumping')" \
    "$old_version" "$new_version" "${#files[@]}"
for f in "${files[@]}"; do
    printf '  - %s\n' "$f"
done

if [[ "$dry_run" == true ]]; then
    printf '\nDry-run complete. No files were modified.\n'
    exit 0
fi

OLD_VERSION="$old_version" NEW_VERSION="$new_version" perl -0pi -e \
    's/\Q$ENV{OLD_VERSION}\E/$ENV{NEW_VERSION}/g' "${files[@]}"

# Verify no occurrences remain in active tracked files
remaining=()
while IFS= read -r line; do
    [[ -n "$line" ]] && remaining+=("$line")
done < <(git grep -Il -F -- "$old_version" -- . "${pathspecs[@]}" || true)

if [[ ${#remaining[@]} -gt 0 ]]; then
    printf 'Error: Version %s still remains in tracked files:\n' "$old_version" >&2
    for r in "${remaining[@]}"; do
        printf '  - %s\n' "$r" >&2
    done
    exit 1
fi

printf '\nSuccessfully updated version to %s.\n' "$new_version"

if [[ "$verify" == true ]]; then
    printf '\nRunning post-bump verification...\n'
    
    # Locate shared or local python virtualenv
    venv_dir=""
    common_git_dir=$(git rev-parse --git-common-dir 2>/dev/null || true)
    if [[ -n "$common_git_dir" && -d "$(cd "$common_git_dir/.." && pwd)/python3.12.venv" ]]; then
        venv_dir="$(cd "$common_git_dir/.." && pwd)/python3.12.venv"
    elif [[ -d "${repo_root}/python3.12.venv" ]]; then
        venv_dir="${repo_root}/python3.12.venv"
    elif [[ -n "${VIRTUAL_ENV:-}" && -d "${VIRTUAL_ENV}" ]]; then
        venv_dir="${VIRTUAL_ENV}"
    fi

    black_bin="black"
    sphinx_bin="sphinx-build"
    pytest_bin="pytest"

    if [[ -n "$venv_dir" ]]; then
        [[ -x "${venv_dir}/bin/black" ]] && black_bin="${venv_dir}/bin/black"
        [[ -x "${venv_dir}/bin/sphinx-build" ]] && sphinx_bin="${venv_dir}/bin/sphinx-build"
        [[ -x "${venv_dir}/bin/pytest" ]] && pytest_bin="${venv_dir}/bin/pytest"
    fi

    # 1. Format check
    if command -v "$black_bin" >/dev/null 2>&1; then
        printf '[1/3] Checking Black formatting on conf.py...\n'
        "$black_bin" --check sphinx_docs_build/source/conf.py
    else
        printf '[1/3] Black not found, skipping format check.\n'
    fi

    # 2. Sphinx doc build check (must pass with zero warnings)
    if command -v "$sphinx_bin" >/dev/null 2>&1; then
        printf '[2/3] Building Sphinx landing documentation (SPHINXOPTS="-W")...\n'
        (cd sphinx_docs_build/landing && SPHINXBUILD="$sphinx_bin" make html SPHINXOPTS="-W" >/dev/null && rm -rf .doctrees)
    else
        printf '[2/3] sphinx-build not found, skipping doc build.\n'
    fi

    # 3. Quick test check
    if command -v "$pytest_bin" >/dev/null 2>&1; then
        printf '[3/3] Running release scripts unit tests...\n'
        "$pytest_bin" .github/scripts/tests/ -q
    else
        printf '[3/3] pytest not found, skipping unit tests.\n'
    fi

    printf 'Verification complete: all checks passed with zero warnings.\n'
fi
