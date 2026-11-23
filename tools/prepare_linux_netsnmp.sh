#!/usr/bin/env bash
set -euo pipefail

# Prepare Net-SNMP 5.10 from the shallow third_party/net-snmp sub-repo (or
# verified archive fallback) for Linux wheel and source builds.
# Matches the Windows standalone strategy by building a minimal, optimized
# shared library (libnetsnmp.so) without daemons or CLI applications.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

NETSNMP_VERSION="${NETSNMP_VERSION:-5.10.rc1}"
EXPECTED_SHA256="${EXPECTED_SHA256:-009cbda7879b1c75cee01df9f4eab2797df47c6c5f90b70aed3e51dce89d8e76}"
PREFIX="${PREFIX:-/usr/local}"
VENDORED_SRC="${EZSNMP_NETSNMP_SOURCE_DIR:-${REPO_ROOT}/third_party/net-snmp}"

echo "=== Preparing Net-SNMP ${NETSNMP_VERSION} for Linux (PREFIX=${PREFIX}) ==="

# Check if already installed with 5.10
if [[ -x "${PREFIX}/bin/net-snmp-config" ]]; then
    INSTALLED_VER=$("${PREFIX}/bin/net-snmp-config" --version || true)
    if [[ "${INSTALLED_VER}" == *"5.10"* ]]; then
        echo "Net-SNMP ${INSTALLED_VER} already installed at ${PREFIX}. Skipping build."
        exit 0
    fi
fi

# Install system dependencies when running as root (unless skipped)
if [[ "${SKIP_PKG_INSTALL:-0}" != "1" ]] && [[ "$(id -u)" -eq 0 ]]; then
    if command -v dnf >/dev/null 2>&1; then
        dnf install -y file openssl-devel perl-ExtUtils-MakeMaker || yum install -y file openssl-devel perl-ExtUtils-MakeMaker
    elif command -v yum >/dev/null 2>&1; then
        yum install -y file openssl-devel perl-ExtUtils-MakeMaker
    elif command -v apt-get >/dev/null 2>&1; then
        apt-get update && apt-get install -y --no-install-recommends file libssl-dev perl make gcc g++ ca-certificates git curl
    elif command -v apk >/dev/null 2>&1; then
        apk add file openssl-dev perl make gcc g++ musl-dev linux-headers git curl
    fi
fi

# Populate shallow sub-repo third_party/net-snmp if not already present
if [[ ! -f "${VENDORED_SRC}/configure" ]]; then
    if command -v python3 >/dev/null 2>&1 && [[ -f "${SCRIPT_DIR}/prepare_netsnmp_source.py" ]]; then
        echo "Provisioning shallow Net-SNMP ${NETSNMP_VERSION} sub-repo via prepare_netsnmp_source.py..."
        python3 "${SCRIPT_DIR}/prepare_netsnmp_source.py" --tag "v${NETSNMP_VERSION}" --target-dir "${VENDORED_SRC}" || true
    elif command -v git >/dev/null 2>&1; then
        echo "Shallow-cloning Net-SNMP v${NETSNMP_VERSION} into ${VENDORED_SRC}..."
        mkdir -p "$(dirname "${VENDORED_SRC}")"
        rm -rf "${VENDORED_SRC}"
        git clone --depth 1 --branch "v${NETSNMP_VERSION}" https://github.com/net-snmp/net-snmp.git "${VENDORED_SRC}" || true
    fi
fi

WORK_DIR=$(mktemp -d /tmp/netsnmp-build-XXXXXX)
trap 'rm -rf "${WORK_DIR}"' EXIT

if [[ -f "${VENDORED_SRC}/configure" ]]; then
    echo "Using shallow Net-SNMP sub-repo from ${VENDORED_SRC}..."
    SOURCE_DIR="${WORK_DIR}/net-snmp-${NETSNMP_VERSION}"
    mkdir -p "${SOURCE_DIR}"
    cp -a "${VENDORED_SRC}/." "${SOURCE_DIR}/"
else
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
fi

cd "${SOURCE_DIR}"

NPROCS=$(nproc 2>/dev/null || echo 2)
DEFAULT_MIBS="IP-MIB:IF-MIB:TCP-MIB:UDP-MIB:SNMPv2-MIB:RFC1213-MIB:NOTIFICATION-LOG-MIB:DISMAN-EVENT-MIB:DISMAN-SCHEDULE-MIB:HOST-RESOURCES-MIB:HOST-RESOURCES-TYPES:UCD-SNMP-MIB:UCD-DEMO-MIB:SNMP-TARGET-MIB:NET-SNMP-AGENT-MIB:NET-SNMP-EXTEND-MIB:SNMP-FRAMEWORK-MIB:SNMP-MPD-MIB:SNMP-USER-BASED-SM-MIB:SNMP-VIEW-BASED-ACM-MIB:SNMP-COMMUNITY-MIB:NET-SNMP-VACM-MIB"
DEFAULT_MIBDIRS="\$HOME/.snmp/mibs:/usr/share/snmp/mibs:/usr/share/snmp/mibs/iana:/usr/share/snmp/mibs/ietf:/usr/local/share/snmp/mibs:/var/lib/snmp/mibs:/var/lib/snmp/mibs/iana:/var/lib/snmp/mibs/ietf"

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

if [[ "$(id -u)" -eq 0 ]] && command -v ldconfig >/dev/null 2>&1; then
    ldconfig "${PREFIX}/lib" 2>/dev/null || true
fi

echo "=== Net-SNMP ${NETSNMP_VERSION} installation complete ==="
"${PREFIX}/bin/net-snmp-config" --version
echo "Default MIBs: $("${PREFIX}/bin/net-snmp-config" --default-mibs)"
echo "Default MIB dirs: $("${PREFIX}/bin/net-snmp-config" --default-mibdirs)"
