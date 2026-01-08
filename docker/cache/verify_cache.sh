#!/bin/bash
# Quick verification script to check if the Docker build cache is working

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CACHE_DIR="${SCRIPT_DIR}"

echo "=== Docker Build Cache Verification ==="
echo ""

# Check if cache directory exists
if [ ! -d "${CACHE_DIR}" ]; then
    echo "❌ ERROR: Cache directory not found at ${CACHE_DIR}"
    exit 1
fi

echo "✓ Cache directory exists: ${CACHE_DIR}"
echo ""

# Define expected files
PYTHON_TARBALLS=(
    "Python-3.10.16.tgz"
    "Python-3.11.11.tgz"
    "Python-3.12.8.tgz"
    "Python-3.13.7.tgz"
    "Python-3.14.2.tgz"
)

OPENSSL_FILES=(
    "openssl-1.1.1w.tar.gz"
)

ARCHLINUX_PACKAGES=(
    "net-snmp-5.7.3-1-x86_64.pkg.tar.xz"
    "net-snmp-5.8-1-x86_64.pkg.tar.xz"
    "pcre-8.43-1-x86_64.pkg.tar.xz"
    "openssl-1.1-1.1.1.w-1-x86_64.pkg.tar.zst"
)

MISSING_COUNT=0
PRESENT_COUNT=0

echo "--- Python Source Tarballs ---"
for tarball in "${PYTHON_TARBALLS[@]}"; do
    if [ -f "${CACHE_DIR}/${tarball}" ]; then
        SIZE=$(du -h "${CACHE_DIR}/${tarball}" | cut -f1)
        echo "  ✓ ${tarball} (${SIZE})"
        ((PRESENT_COUNT++))
    else
        echo "  ❌ ${tarball} - MISSING"
        ((MISSING_COUNT++))
    fi
done

echo ""
echo "--- OpenSSL for CentOS7 ---"
for file in "${OPENSSL_FILES[@]}"; do
    if [ -f "${CACHE_DIR}/${file}" ]; then
        SIZE=$(du -h "${CACHE_DIR}/${file}" | cut -f1)
        echo "  ✓ ${file} (${SIZE})"
        ((PRESENT_COUNT++))
    else
        echo "  ❌ ${file} - MISSING"
        ((MISSING_COUNT++))
    fi
done

echo ""
echo "--- Archlinux Packages (net-snmp 5.7/5.8) ---"
for pkg in "${ARCHLINUX_PACKAGES[@]}"; do
    if [ -f "${CACHE_DIR}/${pkg}" ]; then
        SIZE=$(du -h "${CACHE_DIR}/${pkg}" | cut -f1)
        echo "  ✓ ${pkg} (${SIZE})"
        ((PRESENT_COUNT++))
    else
        echo "  ❌ ${pkg} - MISSING"
        ((MISSING_COUNT++))
    fi
done

TOTAL_EXPECTED=$((${#PYTHON_TARBALLS[@]} + ${#OPENSSL_FILES[@]} + ${#ARCHLINUX_PACKAGES[@]}))

echo ""
echo "=== Summary ==="
echo "Present: ${PRESENT_COUNT}/${TOTAL_EXPECTED}"
echo "Missing: ${MISSING_COUNT}/${TOTAL_EXPECTED}"

if [ ${MISSING_COUNT} -gt 0 ]; then
    echo ""
    echo "⚠ Some files are missing. Run the download script:"
    echo "   ${SCRIPT_DIR}/download_build_cache.sh"
    exit 1
fi

echo ""
echo "Total cache size: $(du -sh "${CACHE_DIR}" | cut -f1)"
echo ""
echo "✓ All build dependencies are cached and ready!"
echo "  You can now build Docker images without downloading external dependencies."
