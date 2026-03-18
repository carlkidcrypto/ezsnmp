#!/bin/bash
set -euo pipefail

# Download all tarballs and packages to a local cache to avoid repeated downloads
# This script should be run before building Docker images

CACHE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Python versions to download
PYTHON_VERSIONS=(
    "3.10.16"
    "3.11.11"
    "3.12.8"
    "3.13.7"
    "3.14.2"
)

# OpenSSL versions
OPENSSL_1_1_VERSION="1.1.1w"
OPENSSL_1_1_URL="https://www.openssl.org/source/openssl-${OPENSSL_1_1_VERSION}.tar.gz"
OPENSSL_1_0_VERSION="1.0.2u"
OPENSSL_1_0_URL="https://www.openssl.org/source/old/1.0.2/openssl-${OPENSSL_1_0_VERSION}.tar.gz"

# SQLite for CentOS7 (Python 3.13+ requires SQLite >= 3.15.2)
SQLITE_VERSION="3450100"  # SQLite 3.45.1
SQLITE_URL="https://www.sqlite.org/2024/sqlite-autoconf-${SQLITE_VERSION}.tar.gz"

# Net-SNMP versions
NETSNMP_VERSIONS=(
    "5.6.4:https://sourceforge.net/projects/net-snmp/files/net-snmp/5.6.4/net-snmp-5.6.4.tar.gz"
    "5.7.3:https://sourceforge.net/projects/net-snmp/files/net-snmp/5.7.3/net-snmp-5.7.3.tar.gz"
    "5.8:https://sourceforge.net/projects/net-snmp/files/net-snmp/5.8/net-snmp-5.8.tar.gz"
    "5.9.4:https://sourceforge.net/projects/net-snmp/files/net-snmp/5.9.4/net-snmp-5.9.4.tar.gz"
)

# GoogleTest for CentOS8
GTEST_VERSION="1.15.2"
GTEST_URL="https://github.com/google/googletest/archive/refs/tags/v${GTEST_VERSION}.tar.gz"

# Archlinux packages for net-snmp compatibility testing
ARCHLINUX_PACKAGES=(
    "https://archive.archlinux.org/packages/n/net-snmp/net-snmp-5.7.3-1-x86_64.pkg.tar.xz"
    "https://archive.archlinux.org/packages/n/net-snmp/net-snmp-5.8-1-x86_64.pkg.tar.xz"
    "https://archive.archlinux.org/packages/p/pcre/pcre-8.43-1-x86_64.pkg.tar.xz"
    "https://archive.archlinux.org/packages/o/openssl-1.0/openssl-1.0-1.0.2.t-1-x86_64.pkg.tar.xz"
    "https://archive.archlinux.org/packages/o/openssl-1.1/openssl-1.1-1.1.1.w-1-x86_64.pkg.tar.zst"
)

echo "=== Docker Build Cache Downloader ==="
echo "Cache directory: ${CACHE_DIR}"
echo ""

# Portable download function: prefers wget, falls back to curl (macOS default).
# Downloads to a .part file first, supporting resume of interrupted downloads.
# Resume flags (-c / -C -) allow wget/curl to continue a partial .part file,
# which avoids re-downloading already-transferred data and helps with slow CDNs
# (e.g. SourceForge mirrors that stall mid-transfer).
# The caller is responsible for removing a corrupt output file before calling
# this function; fetch_tarball() does that automatically.
download() {
    local url="$1"
    local output="$2"
    local partial="${output}.part"

    if command -v wget &>/dev/null; then
        wget \
            -q --show-progress \
            --tries=8 \
            --retry-connrefused \
            --waitretry=2 \
            --dns-timeout=15 \
            --connect-timeout=20 \
            --read-timeout=30 \
            --timeout=30 \
            -c \
            "${url}" -O "${partial}"
    elif command -v curl &>/dev/null; then
        curl \
            -L --progress-bar \
            --retry 8 \
            --retry-delay 2 \
            --retry-connrefused \
            --connect-timeout 20 \
            --max-time 1800 \
            --speed-time 30 \
            --speed-limit 1024 \
            -C - \
            -o "${partial}" "${url}"
    else
        echo "ERROR: Neither wget nor curl is available. Please install one of them."
        exit 1
    fi

    mv -f "${partial}" "${output}"
}

# Validate that a .tar.gz / .tgz file can be read by gzip.
# Returns 0 (true) if the file is a valid gzip archive, 1 otherwise.
is_valid_tarball() {
    local file="$1"
    gzip -t "${file}" 2>/dev/null
}

# Return 0 (true) if a file exists AND passes tarball validation.
is_cached_and_valid() {
    local file="$1"
    [ -f "${file}" ] && is_valid_tarball "${file}"
}

# Download a tarball only if it is missing or corrupt.
# Usage: fetch_tarball <url> <output_path>
fetch_tarball() {
    local url="$1"
    local output="$2"
    local filename
    filename=$(basename "${output}")

    if is_cached_and_valid "${output}"; then
        echo "✓ ${filename} already cached"
    else
        if [ -f "${output}" ]; then
            echo "⚠ ${filename} exists but is corrupt — re-downloading..."
            # Remove both the corrupt output and any stale .part file so that
            # the resume flags start clean instead of appending to garbage.
            rm -f "${output}" "${output}.part"
        else
            echo "⬇ Downloading ${filename}..."
        fi
        download "${url}" "${output}"
        if ! is_valid_tarball "${output}"; then
            echo "ERROR: Downloaded ${filename} failed integrity check (corrupt gzip)."
            rm -f "${output}"
            exit 1
        fi
        echo "✓ Downloaded ${filename}"
    fi
}

# Create cache directory if it doesn't exist
mkdir -p "${CACHE_DIR}"

# Download Python tarballs
echo "--- Python Source Tarballs ---"
for version in "${PYTHON_VERSIONS[@]}"; do
    tarball="Python-${version}.tgz"
    url="https://www.python.org/ftp/python/${version}/${tarball}"
    fetch_tarball "${url}" "${CACHE_DIR}/${tarball}"
done

echo ""
echo "--- OpenSSL and SQLite ---"
# Download OpenSSL 1.1.1w (for CentOS7)
fetch_tarball "${OPENSSL_1_1_URL}" "${CACHE_DIR}/openssl-${OPENSSL_1_1_VERSION}.tar.gz"

# Download OpenSSL 1.0.2u (for Archlinux Net-SNMP 5.7.3)
fetch_tarball "${OPENSSL_1_0_URL}" "${CACHE_DIR}/openssl-${OPENSSL_1_0_VERSION}.tar.gz"

# Download SQLite
fetch_tarball "${SQLITE_URL}" "${CACHE_DIR}/sqlite-autoconf-${SQLITE_VERSION}.tar.gz"

echo ""
echo "--- Net-SNMP Source Tarballs ---"
for entry in "${NETSNMP_VERSIONS[@]}"; do
    url="${entry#*:}"
    filename=$(basename "${url}")
    fetch_tarball "${url}" "${CACHE_DIR}/${filename}"
done

echo ""
echo "--- GoogleTest (for CentOS8) ---"
fetch_tarball "${GTEST_URL}" "${CACHE_DIR}/v${GTEST_VERSION}.tar.gz"

echo ""
echo "--- Archlinux Packages (for net-snmp 5.7/5.8 compatibility) ---"
# Download Archlinux packages (these are .pkg.tar.xz/.pkg.tar.zst, not gzip; skip tarball validation)
for pkg_url in "${ARCHLINUX_PACKAGES[@]}"; do
    pkg_file=$(basename "${pkg_url}")
    pkg_output="${CACHE_DIR}/${pkg_file}"

    if [ -f "${pkg_output}" ]; then
        echo "✓ ${pkg_file} already cached"
    else
        echo "⬇ Downloading ${pkg_file}..."
        download "${pkg_url}" "${pkg_output}"
        echo "✓ Downloaded ${pkg_file}"
    fi
done

echo ""
echo "=== Cache Summary ==="
echo "Python tarballs:"
ls -lh "${CACHE_DIR}"/Python-*.tgz 2>/dev/null || echo "  No Python tarballs found"
echo ""
echo "OpenSSL and SQLite:"
ls -lh "${CACHE_DIR}"/openssl-*.tar.gz "${CACHE_DIR}"/sqlite-*.tar.gz 2>/dev/null || echo "  No OpenSSL/SQLite tarballs found"
echo ""
echo "Net-SNMP tarballs:"
ls -lh "${CACHE_DIR}"/net-snmp-*.tar.gz 2>/dev/null || echo "  No Net-SNMP tarballs found"
echo ""
echo "GoogleTest:"
ls -lh "${CACHE_DIR}"/v*.tar.gz 2>/dev/null || echo "  No GoogleTest tarball found"
echo ""
echo "Archlinux packages:"
ls -lh "${CACHE_DIR}"/*.pkg.tar.* 2>/dev/null || echo "  No Archlinux packages found"
echo ""
echo "Total cache size: $(du -sh "${CACHE_DIR}" | cut -f1)"
echo ""
echo "✓ Cache is ready!"
