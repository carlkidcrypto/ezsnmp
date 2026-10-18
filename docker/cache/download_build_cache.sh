#!/bin/bash
set -euo pipefail

# Download all tarballs and packages to a local cache to avoid repeated downloads
# This script should be run before building Docker images

CACHE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Python versions to download
PYTHON_VERSIONS=(
    "3.10.21"
    "3.11.16"
    "3.12.14"
    "3.13.15"
    "3.14.7"
)

# Net-SNMP versions (for test container builds)
NETSNMP_VERSIONS=(
    "5.9.5.2:https://sourceforge.net/projects/net-snmp/files/net-snmp/5.9.5.2/net-snmp-5.9.5.2.tar.gz"
)


echo "=== Docker Build Cache Downloader ==="
echo "Cache directory: ${CACHE_DIR}"
echo ""

# Download helper: use wget when available, otherwise fall back to curl (macOS default)
download() {
    local url="$1"
    local output="$2"

    if command -v wget >/dev/null 2>&1; then
        if ! wget -q --show-progress \
            --tries=3 \
            --retry-connrefused \
            --waitretry=2 \
            --dns-timeout=15 \
            --connect-timeout=20 \
            --read-timeout=60 \
            --timeout=60 \
            "${url}" -O "${output}"; then
            rm -f "${output}"
            return 1
        fi
    elif command -v curl >/dev/null 2>&1; then
        if ! curl -L --progress-bar \
            --fail \
            --retry 3 \
            --retry-delay 2 \
            --retry-connrefused \
            --connect-timeout 20 \
            --max-time 600 \
            --speed-time 30 \
            --speed-limit 1024 \
            -o "${output}" "${url}"; then
            rm -f "${output}"
            return 1
        fi
    else
        echo "ERROR: Neither wget nor curl is available."
        exit 1
    fi
}

# Resolve the best available Net-SNMP tag URL from GitHub for a requested version.
# Order:
# 1) exact tag v<version>
# 2) exact tag with common patch suffixes (v<version>.1, v<version>.2)
# 3) nearest stable tag in same major.minor line (e.g. v5.7.3-1 for 5.7.x)
resolve_netsnmp_github_tag() {
    local requested_version="$1"
    local major_minor
    local chosen_tag=""

    major_minor="$(echo "${requested_version}" | awk -F. '{print $1"."$2}')"

    # Cache tag list for this script run.
    if [ -z "${NETSNMP_TAG_CACHE:-}" ]; then
        NETSNMP_TAG_CACHE="$({
            git ls-remote --tags https://github.com/net-snmp/net-snmp.git 2>/dev/null || true
        } | awk '{print $2}' | sed 's#refs/tags/##' | sed 's/\^{}$//' | sort -u)"
    fi

    # Exact candidates first.
    for candidate in "v${requested_version}" "v${requested_version}.1" "v${requested_version}.2"; do
        if printf '%s\n' "${NETSNMP_TAG_CACHE}" | grep -Fxq "${candidate}"; then
            chosen_tag="${candidate}"
            break
        fi
    done

    # Fallback to latest stable tag in same major.minor family.
    if [ -z "${chosen_tag}" ]; then
        chosen_tag="$(printf '%s\n' "${NETSNMP_TAG_CACHE}" \
            | grep -E "^v${major_minor}(\.[0-9]+)*$" \
            | sort -V \
            | tail -n 1)"
    fi

    printf '%s' "${chosen_tag}"
}

# Create cache directory if it doesn't exist
mkdir -p "${CACHE_DIR}"

# Download Python tarballs
echo "--- Python Source Tarballs ---"
for version in "${PYTHON_VERSIONS[@]}"; do
    tarball="Python-${version}.tgz"
    url="https://www.python.org/ftp/python/${version}/${tarball}"
    output="${CACHE_DIR}/${tarball}"
    
    if [ -f "${output}" ]; then
        echo "✓ ${tarball} already cached"
    else
        echo "⬇ Downloading ${tarball}..."
        download "${url}" "${output}"
        echo "✓ Downloaded ${tarball}"
    fi
done


echo ""

echo "--- Net-SNMP Source Tarballs ---"
for entry in "${NETSNMP_VERSIONS[@]}"; do
    version="${entry%%:*}"
    url="${entry#*:}"
    filename=$(basename "${url}")
    output="${CACHE_DIR}/${filename}"
    
    if [ -f "${output}" ]; then
        echo "✓ ${filename} already cached"
    else
        echo "⬇ Downloading ${filename}..."
        if ! download "${url}" "${output}"; then
            echo "WARN: Primary download failed for ${filename}. Trying GitHub tag fallback..."
            rm -f "${output}"

            github_tag="$(resolve_netsnmp_github_tag "${version}")"
            if [ -z "${github_tag}" ]; then
                rm -f "${output}"
                echo "ERROR: Could not resolve a GitHub tag fallback for net-snmp ${version}."
                echo "       Check available tags at: https://github.com/net-snmp/net-snmp/tags"
                exit 1
            fi

            github_fallback_url="https://github.com/net-snmp/net-snmp/archive/refs/tags/${github_tag}.tar.gz"
            github_codeload_url="https://codeload.github.com/net-snmp/net-snmp/tar.gz/refs/tags/${github_tag}"

            echo "      - Trying ${github_fallback_url}"
            if ! download "${github_fallback_url}" "${output}"; then
                rm -f "${output}"
                echo "      - Trying ${github_codeload_url}"
            fi

            if [ ! -f "${output}" ] || [ ! -s "${output}" ]; then
                if ! download "${github_codeload_url}" "${output}"; then
                    rm -f "${output}"
                fi
            fi

            if [ ! -f "${output}" ] || [ ! -s "${output}" ]; then
                rm -f "${output}"
                echo "ERROR: Failed to download ${filename} from both SourceForge and GitHub fallback."
                exit 1
            fi

            if [ "${github_tag}" != "v${version}" ]; then
                echo "WARN: Requested ${version}, but GitHub fallback resolved to ${github_tag}."
            fi
        fi
        echo "✓ Downloaded ${filename}"
    fi
done

echo ""
echo "=== Cache Summary ==="
echo "Python tarballs:"
ls -lh "${CACHE_DIR}"/Python-*.tgz 2>/dev/null || echo "  No Python tarballs found"
echo ""
echo "Net-SNMP tarballs:"
ls -lh "${CACHE_DIR}"/net-snmp-*.tar.gz 2>/dev/null || echo "  No Net-SNMP tarballs found"
echo ""
echo "Total cache size: $(du -sh "${CACHE_DIR}" | cut -f1)"

echo ""
echo "✓ Cache is ready!"