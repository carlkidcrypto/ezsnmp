#!/usr/bin/env bash
set -euo pipefail

# Prepare Net-SNMP 5.10 from source for Linux wheel builds (cibuildwheel).
# Matches the Windows standalone strategy by building a minimal, optimized
# shared library (libnetsnmp.so) without daemons or CLI applications.

NETSNMP_VERSION="5.10.pre2"
EXPECTED_SHA256="6bce4ef368db15ad0f400330d5a1433009d63f0a98ca8b2eca0f87abd3469bd6"
PREFIX="/usr/local"

echo "=== Preparing Net-SNMP ${NETSNMP_VERSION} for Linux ==="

# Check if already installed with 5.10
if [[ -x "${PREFIX}/bin/net-snmp-config" ]]; then
    INSTALLED_VER=$("${PREFIX}/bin/net-snmp-config" --version || true)
    if [[ "${INSTALLED_VER}" == *"5.10"* ]]; then
        echo "Net-SNMP ${INSTALLED_VER} already installed at ${PREFIX}. Skipping build."
        exit 0
    fi
fi

# Install system dependencies based on package manager
if command -v dnf >/dev/null 2>&1; then
    dnf install -y openssl-devel perl-ExtUtils-MakeMaker || yum install -y openssl-devel perl-ExtUtils-MakeMaker
elif command -v yum >/dev/null 2>&1; then
    yum install -y openssl-devel perl-ExtUtils-MakeMaker
elif command -v apt-get >/dev/null 2>&1; then
    apt-get update && apt-get install -y libssl-dev perl
elif command -v apk >/dev/null 2>&1; then
    apk add openssl-dev perl make gcc g++ musl-dev linux-headers
fi

WORK_DIR=$(mktemp -d /tmp/netsnmp-build-XXXXXX)
trap 'rm -rf "${WORK_DIR}"' EXIT

ARCHIVE_PATH="${WORK_DIR}/v${NETSNMP_VERSION}.tar.gz"
DOWNLOAD_URL="https://github.com/net-snmp/net-snmp/archive/refs/tags/v${NETSNMP_VERSION}.tar.gz"

echo "Downloading Net-SNMP from ${DOWNLOAD_URL}..."
curl --proto '=https' --proto-redir '=https' -sSL -o "${ARCHIVE_PATH}" "${DOWNLOAD_URL}"

echo "Verifying SHA256 checksum..."
ACTUAL_SHA256=$(sha256sum "${ARCHIVE_PATH}" | awk '{print $1}')
if [[ "${ACTUAL_SHA256}" != "${EXPECTED_SHA256}" ]]; then
    echo "ERROR: SHA256 mismatch! Expected ${EXPECTED_SHA256}, got ${ACTUAL_SHA256}" >&2
    exit 1
fi

echo "Extracting Net-SNMP archive..."
tar -xzf "${ARCHIVE_PATH}" -C "${WORK_DIR}"
SOURCE_DIR="${WORK_DIR}/net-snmp-${NETSNMP_VERSION}"

cd "${SOURCE_DIR}"

NPROCS=$(nproc 2>/dev/null || echo 2)
DEFAULT_MIBS="IP-MIB:IF-MIB:TCP-MIB:UDP-MIB:SNMPv2-MIB:RFC1213-MIB:NOTIFICATION-LOG-MIB:DISMAN-EVENT-MIB:DISMAN-SCHEDULE-MIB:HOST-RESOURCES-MIB:HOST-RESOURCES-TYPES:UCD-SNMP-MIB:UCD-DEMO-MIB:SNMP-TARGET-MIB:NET-SNMP-AGENT-MIB:NET-SNMP-EXTEND-MIB:SNMP-FRAMEWORK-MIB:SNMP-MPD-MIB:SNMP-USER-BASED-SM-MIB:SNMP-VIEW-BASED-ACM-MIB:SNMP-COMMUNITY-MIB:NET-SNMP-VACM-MIB"
DEFAULT_MIBDIRS="\$HOME/.snmp/mibs:/usr/share/snmp/mibs:/usr/local/share/snmp/mibs"

echo "Configuring Net-SNMP ${NETSNMP_VERSION} with minimal shared-library options..."
./configure \
    --prefix="${PREFIX}" \
    --with-defaults \
    --with-mibs="${DEFAULT_MIBS}" \
    --with-mibdirs="${DEFAULT_MIBDIRS}" \
    --enable-shared \
    --disable-static \
    --disable-agent \
    --disable-applications \
    --disable-manuals \
    --disable-scripts \
    --disable-mibs \
    --without-perl-modules \
    --disable-embedded-perl \
    --with-openssl \
    --enable-blumenthal-aes

echo "Compiling Net-SNMP (parallelism: ${NPROCS})..."
make -j"${NPROCS}"

echo "Installing Net-SNMP to ${PREFIX}..."
make install

if command -v ldconfig >/dev/null 2>&1; then
    ldconfig "${PREFIX}/lib" 2>/dev/null || true
fi

echo "=== Net-SNMP ${NETSNMP_VERSION} installation complete ==="
"${PREFIX}/bin/net-snmp-config" --version
echo "Default MIBs: $("${PREFIX}/bin/net-snmp-config" --default-mibs)"
echo "Default MIB dirs: $("${PREFIX}/bin/net-snmp-config" --default-mibdirs)"
