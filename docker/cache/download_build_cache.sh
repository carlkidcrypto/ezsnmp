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
        wget -q --show-progress "${url}" -O "${output}"
        echo "✓ Downloaded ${tarball}"
    fi
done

echo ""
echo "--- OpenSSL and SQLite ---"
# Download OpenSSL 1.1.1w (for CentOS7)
openssl_1_1_file="openssl-${OPENSSL_1_1_VERSION}.tar.gz"
openssl_1_1_output="${CACHE_DIR}/${openssl_1_1_file}"
if [ -f "${openssl_1_1_output}" ]; then
    echo "✓ ${openssl_1_1_file} already cached"
else
    echo "⬇ Downloading ${openssl_1_1_file}..."
    wget -q --show-progress "${OPENSSL_1_1_URL}" -O "${openssl_1_1_output}"
    echo "✓ Downloaded ${openssl_1_1_file}"
fi

# Download OpenSSL 1.0.2u (for Archlinux Net-SNMP 5.7.3)
openssl_1_0_file="openssl-${OPENSSL_1_0_VERSION}.tar.gz"
openssl_1_0_output="${CACHE_DIR}/${openssl_1_0_file}"
if [ -f "${openssl_1_0_output}" ]; then
    echo "✓ ${openssl_1_0_file} already cached"
else
    echo "⬇ Downloading ${openssl_1_0_file}..."
    wget -q --show-progress "${OPENSSL_1_0_URL}" -O "${openssl_1_0_output}"
    echo "✓ Downloaded ${openssl_1_0_file}"
fi

# Download SQLite
sqlite_file="sqlite-autoconf-${SQLITE_VERSION}.tar.gz"
sqlite_output="${CACHE_DIR}/${sqlite_file}"
if [ -f "${sqlite_output}" ]; then
    echo "✓ ${sqlite_file} already cached"
else
    echo "⬇ Downloading ${sqlite_file}..."
    wget -q --show-progress "${SQLITE_URL}" -O "${sqlite_output}"
    echo "✓ Downloaded ${sqlite_file}"
fi

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
        wget -q --show-progress "${url}" -O "${output}"
        echo "✓ Downloaded ${filename}"
    fi
done

echo ""
echo "--- GoogleTest (for CentOS8) ---"
gtest_file="v${GTEST_VERSION}.tar.gz"
gtest_output="${CACHE_DIR}/${gtest_file}"
if [ -f "${gtest_output}" ]; then
    echo "✓ ${gtest_file} already cached"
else
    echo "⬇ Downloading ${gtest_file}..."
    wget -q --show-progress "${GTEST_URL}" -O "${gtest_output}"
    echo "✓ Downloaded ${gtest_file}"
fi

echo ""
echo "--- Archlinux Packages (for net-snmp 5.7/5.8 compatibility) ---"
# Download Archlinux packages
for pkg_url in "${ARCHLINUX_PACKAGES[@]}"; do
    pkg_file=$(basename "${pkg_url}")
    pkg_output="${CACHE_DIR}/${pkg_file}"
    
    if [ -f "${pkg_output}" ]; then
        echo "✓ ${pkg_file} already cached"
    else
        echo "⬇ Downloading ${pkg_file}..."
        wget -q --show-progress "${pkg_url}" -O "${pkg_output}"
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
