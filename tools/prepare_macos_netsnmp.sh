#!/usr/bin/env bash
set -euo pipefail

NETSNMP_VERSION="5.10.pre2"
EXPECTED_SHA256="6bce4ef368db15ad0f400330d5a1433009d63f0a98ca8b2eca0f87abd3469bd6"
PREFIX="/usr/local"
MACPORTS_PREFIX="/opt/local"

if [[ -x "${PREFIX}/bin/net-snmp-config" ]]; then
    INSTALLED_VER=$("${PREFIX}/bin/net-snmp-config" --version || true)
    if [[ "${INSTALLED_VER}" == *"5.10"* ]]; then
        echo "Net-SNMP ${INSTALLED_VER} already installed at ${PREFIX}. Skipping build."
        exit 0
    fi
fi

WORK_DIR=$(mktemp -d "${TMPDIR:-/tmp}/netsnmp-build.XXXXXX")
trap 'rm -rf "${WORK_DIR}"' EXIT

ARCHIVE_PATH="${WORK_DIR}/v${NETSNMP_VERSION}.tar.gz"
DOWNLOAD_URL="https://github.com/net-snmp/net-snmp/archive/refs/tags/v${NETSNMP_VERSION}.tar.gz"

echo "Downloading Net-SNMP from ${DOWNLOAD_URL}..."
curl --proto '=https' --proto-redir '=https' -sSL -o "${ARCHIVE_PATH}" "${DOWNLOAD_URL}"

echo "Verifying SHA256 checksum..."
ACTUAL_SHA256=$(shasum -a 256 "${ARCHIVE_PATH}" | awk '{print $1}')
if [[ "${ACTUAL_SHA256}" != "${EXPECTED_SHA256}" ]]; then
    echo "ERROR: SHA256 mismatch! Expected ${EXPECTED_SHA256}, got ${ACTUAL_SHA256}" >&2
    exit 1
fi

tar -xzf "${ARCHIVE_PATH}" -C "${WORK_DIR}"
SOURCE_DIR="${WORK_DIR}/net-snmp-${NETSNMP_VERSION}"
cd "${SOURCE_DIR}"

NPROCS=$(sysctl -n hw.ncpu 2>/dev/null || echo 2)
DEFAULT_MIBS="IP-MIB:IF-MIB:TCP-MIB:UDP-MIB:SNMPv2-MIB:RFC1213-MIB:NOTIFICATION-LOG-MIB:DISMAN-EVENT-MIB:DISMAN-SCHEDULE-MIB:HOST-RESOURCES-MIB:HOST-RESOURCES-TYPES:UCD-SNMP-MIB:UCD-DEMO-MIB:SNMP-TARGET-MIB:NET-SNMP-AGENT-MIB:NET-SNMP-EXTEND-MIB:SNMP-FRAMEWORK-MIB:SNMP-MPD-MIB:SNMP-USER-BASED-SM-MIB:SNMP-VIEW-BASED-ACM-MIB:SNMP-COMMUNITY-MIB:NET-SNMP-VACM-MIB"
DEFAULT_MIBDIRS="\$HOME/.snmp/mibs:${MACPORTS_PREFIX}/share/snmp/mibs:${PREFIX}/share/snmp/mibs"

CPPFLAGS="-I${MACPORTS_PREFIX}/include ${CPPFLAGS:-}" \
LDFLAGS="-L${MACPORTS_PREFIX}/lib ${LDFLAGS:-}" \
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
    --with-openssl="${MACPORTS_PREFIX}" \
    --enable-blumenthal-aes

make -j"${NPROCS}"
make install

echo "Net-SNMP ${NETSNMP_VERSION} installed at ${PREFIX}."
"${PREFIX}/bin/net-snmp-config" --version
