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

# OpenSSL for CentOS7
OPENSSL_VERSION="1.1.1w"
OPENSSL_URL="https://www.openssl.org/source/openssl-${OPENSSL_VERSION}.tar.gz"

# Archlinux packages for net-snmp compatibility testing
ARCHLINUX_PACKAGES=(
    "https://archive.archlinux.org/packages/n/net-snmp/net-snmp-5.7.3-1-x86_64.pkg.tar.xz"
    "https://archive.archlinux.org/packages/n/net-snmp/net-snmp-5.8-1-x86_64.pkg.tar.xz"
    "https://archive.archlinux.org/packages/p/pcre/pcre-8.43-1-x86_64.pkg.tar.xz"
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
echo "--- OpenSSL for CentOS7 ---"
# Download OpenSSL
openssl_file="openssl-${OPENSSL_VERSION}.tar.gz"
openssl_output="${CACHE_DIR}/${openssl_file}"
if [ -f "${openssl_output}" ]; then
    echo "✓ ${openssl_file} already cached"
else
    echo "⬇ Downloading ${openssl_file}..."
    wget -q --show-progress "${OPENSSL_URL}" -O "${openssl_output}"
    echo "✓ Downloaded ${openssl_file}"
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
echo "OpenSSL:"
ls -lh "${CACHE_DIR}"/openssl-*.tar.gz 2>/dev/null || echo "  No OpenSSL tarballs found"
echo ""
echo "Archlinux packages:"
ls -lh "${CACHE_DIR}"/*.pkg.tar.* 2>/dev/null || echo "  No Archlinux packages found"
echo ""
echo "Total cache size: $(du -sh "${CACHE_DIR}" | cut -f1)"
echo ""
echo "✓ Cache is ready!"
