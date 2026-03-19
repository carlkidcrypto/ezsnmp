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
    "5.6.2.1:https://sourceforge.net/projects/net-snmp/files/net-snmp/5.6.2.1/net-snmp-5.6.2.1.tar.gz"
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
# 3) nearest stable tag in same major.minor line (e.g. v5.6.2.1 for 5.6.x)
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
echo "--- OpenSSL and SQLite ---"
# Download OpenSSL 1.1.1w (for CentOS7)
openssl_1_1_file="openssl-${OPENSSL_1_1_VERSION}.tar.gz"
openssl_1_1_output="${CACHE_DIR}/${openssl_1_1_file}"
if [ -f "${openssl_1_1_output}" ]; then
    echo "✓ ${openssl_1_1_file} already cached"
else
    echo "⬇ Downloading ${openssl_1_1_file}..."
    download "${OPENSSL_1_1_URL}" "${openssl_1_1_output}"
    echo "✓ Downloaded ${openssl_1_1_file}"
fi

# Download OpenSSL 1.0.2u (for Archlinux Net-SNMP 5.7.3)
openssl_1_0_file="openssl-${OPENSSL_1_0_VERSION}.tar.gz"
openssl_1_0_output="${CACHE_DIR}/${openssl_1_0_file}"
if [ -f "${openssl_1_0_output}" ]; then
    echo "✓ ${openssl_1_0_file} already cached"
else
    echo "⬇ Downloading ${openssl_1_0_file}..."
    download "${OPENSSL_1_0_URL}" "${openssl_1_0_output}"
    echo "✓ Downloaded ${openssl_1_0_file}"
fi

# Download SQLite
sqlite_file="sqlite-autoconf-${SQLITE_VERSION}.tar.gz"
sqlite_output="${CACHE_DIR}/${sqlite_file}"
if [ -f "${sqlite_output}" ]; then
    echo "✓ ${sqlite_file} already cached"
else
    echo "⬇ Downloading ${sqlite_file}..."
    download "${SQLITE_URL}" "${sqlite_output}"
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
echo "--- GoogleTest (for CentOS8) ---"
gtest_file="v${GTEST_VERSION}.tar.gz"
gtest_output="${CACHE_DIR}/${gtest_file}"
if [ -f "${gtest_output}" ]; then
    echo "✓ ${gtest_file} already cached"
else
    echo "⬇ Downloading ${gtest_file}..."
    download "${GTEST_URL}" "${gtest_output}"
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