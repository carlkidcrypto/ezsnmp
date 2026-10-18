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
NETSNMP_VERSION="5.10.pre2"
NETSNMP_URL="https://github.com/net-snmp/net-snmp/archive/refs/tags/v${NETSNMP_VERSION}.tar.gz"
NETSNMP_TARBALL="net-snmp-${NETSNMP_VERSION}.tar.gz"

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
output="${CACHE_DIR}/${NETSNMP_TARBALL}"
if [ -f "${output}" ]; then
    echo "✓ ${NETSNMP_TARBALL} already cached"
else
    echo "⬇ Downloading ${NETSNMP_TARBALL} from ${NETSNMP_URL}..."
    download "${NETSNMP_URL}" "${output}"
    echo "✓ Downloaded ${NETSNMP_TARBALL}"
fi

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