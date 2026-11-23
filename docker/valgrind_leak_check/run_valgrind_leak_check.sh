#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
IMAGE_NAME="${EZSNMP_VALGRIND_IMAGE:-ezsnmp-valgrind-trixie:latest}"
CACHE_VOLUME="${EZSNMP_VALGRIND_CACHE_VOLUME:-ezsnmp-valgrind-netsnmp-510-cache}"
ITERS="${EZSNMP_VALGRIND_ITERS:-50}"
RSS_ITERS="${EZSNMP_RSS_ITERS:-1000}"

echo "Ensuring shallow Net-SNMP 5.10 sub-repo (third_party/net-snmp) is populated..."
python3 "${REPO_ROOT}/tools/prepare_netsnmp_source.py"

echo "Building Docker image ${IMAGE_NAME}..."
docker build -t "${IMAGE_NAME}" "${SCRIPT_DIR}"

echo "Running Valgrind + RSS leak check with Net-SNMP 5.10 inside ${IMAGE_NAME}..."
docker run --rm \
  -v "${REPO_ROOT}:/ezsnmp:ro" \
  -v "${CACHE_VOLUME}:/netsnmp_cache" \
  -e "ITERS=${ITERS}" \
  -e "RSS_ITERS=${RSS_ITERS}" \
  "${IMAGE_NAME}" bash -c '
set -euo pipefail

mkdir -p /tmp/ezsnmp_src
tar -C /ezsnmp --exclude="./third_party" --exclude="./.git" --exclude="./build" -cf - . | tar -C /tmp/ezsnmp_src -xf -
cd /tmp/ezsnmp_src
rm -rf build dist ezsnmp.egg-info ezsnmp/*.so
mkdir -p third_party
ln -s /netsnmp_cache third_party/net-snmp-install
export EZSNMP_NETSNMP_SOURCE_DIR=/ezsnmp/third_party/net-snmp

echo "=== Building and installing ezsnmp from source (auto-provisioning Net-SNMP 5.10 from third_party/net-snmp) ==="
SKIP_PKG_INSTALL=1 python3 -m pip install --no-build-isolation --no-deps .

cd /tmp
echo "=== Active Net-SNMP library version linked into ezsnmp ==="
/tmp/ezsnmp_src/third_party/net-snmp-install/bin/net-snmp-config --version
ldd "$(python3 -c "import ezsnmp._sessionbase as s; print(s.__file__)")" | grep netsnmp

printf "rocommunity public 127.0.0.1\nagentaddress udp:127.0.0.1:16101\n" > /tmp/snmpd.conf
snmpd -f -C -c /tmp/snmpd.conf -Lo >/tmp/snmpd.log 2>&1 &
SNMPD_PID=$!
trap "kill ${SNMPD_PID} 2>/dev/null || true" EXIT
sleep 1

echo "=== 1. RSS Growth Check (${RSS_ITERS} iterations per mode) ==="
for mode in open get walk shared; do
  python3 /tmp/ezsnmp_src/docker/valgrind_leak_check/leak_repro.py "${mode}" "${RSS_ITERS}"
done

echo "=== 2. Valgrind Memcheck (${ITERS} iterations per mode) ==="
for mode in get walk; do
  LOG="/tmp/valgrind_${mode}.out"
  PYTHONMALLOC=malloc valgrind \
    --tool=memcheck \
    --leak-check=full \
    --show-leak-kinds=definite,indirect \
    --suppressions=/tmp/valgrind-python.supp \
    --log-file="${LOG}" \
    python3 /tmp/ezsnmp_src/docker/valgrind_leak_check/leak_repro.py "${mode}" "${ITERS}"

  echo "--- Valgrind summary for mode=${mode} ---"
  grep -E "LEAK SUMMARY|definitely lost:|indirectly lost:|ERROR SUMMARY" "${LOG}" || true

  python3 - "${LOG}" "${mode}" << "PY"
import pathlib, re, sys
log_path = pathlib.Path(sys.argv[1])
mode = sys.argv[2]
text = log_path.read_text(errors="replace")
blocks = re.split(r"\n==\d+==\s*\n", text)
markers = (
    "netsnmp_init_mib_internals",
    "netsnmp_parse_args",
    "_sessionbase",
    "_netsnmpbase",
    "SessionBase::",
)
leaks = [
    b.strip()
    for b in blocks
    if re.search(r"bytes in \d+ blocks are (?:definitely|indirectly) lost", b)
    and "PyInit_" not in b
    and any(m in b for m in markers)
]
if leaks:
    print(f"FAIL: mode={mode} leaked {len(leaks)} native ezsnmp/Net-SNMP block(s):", file=sys.stderr)
    for lk in leaks[:5]:
        print(lk, "\n---", file=sys.stderr)
    sys.exit(1)
print(f"PASS: mode={mode} has 0 native ezsnmp/Net-SNMP leaked blocks under Valgrind!")
PY
done
'
