import socket
import threading
import pytest

from ezsnmp import snmpdf as top_level_snmpdf
from ezsnmp.exceptions import GenericError, ParseError, TimeoutError
from ezsnmp.netsnmp import snmpdf


def _encode_len(n: int) -> bytes:
    if n < 0x80:
        return bytes([n])
    b = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(b)]) + b


def _tlv(tag: int, payload: bytes) -> bytes:
    return bytes([tag]) + _encode_len(len(payload)) + payload


def _encode_int(val: int) -> bytes:
    if val == 0:
        return _tlv(0x02, b"\x00")
    length = (val.bit_length() + 8) // 8
    return _tlv(0x02, val.to_bytes(length, "big", signed=True))


def _encode_oid(oid: tuple[int, ...]) -> bytes:
    out = bytearray([oid[0] * 40 + oid[1]])
    for sub in oid[2:]:
        parts = [sub & 0x7F]
        sub >>= 7
        while sub:
            parts.append((sub & 0x7F) | 0x80)
            sub >>= 7
        out.extend(reversed(parts))
    return _tlv(0x06, bytes(out))


def _read_len(buf: bytes, pos: int) -> tuple[int, int]:
    first = buf[pos]
    pos += 1
    if not (first & 0x80):
        return first, pos
    n = first & 0x7F
    return int.from_bytes(buf[pos : pos + n], "big"), pos + n


def _read_int(buf: bytes, pos: int) -> tuple[int, int]:
    assert buf[pos] == 0x02
    length, pos = _read_len(buf, pos + 1)
    return int.from_bytes(buf[pos : pos + length], "big", signed=True), pos + length


def _read_oid(buf: bytes, pos: int) -> tuple[tuple[int, ...], int]:
    assert buf[pos] == 0x06
    length, pos = _read_len(buf, pos + 1)
    end = pos + length
    oids = [buf[pos] // 40, buf[pos] % 40]
    pos += 1
    while pos < end:
        sub = 0
        while True:
            b = buf[pos]
            pos += 1
            sub = (sub << 7) | (b & 0x7F)
            if not (b & 0x80):
                break
        oids.append(sub)
    return tuple(oids), pos


def _decode_request(buf: bytes) -> tuple[int, bytes, int, int, list[tuple[int, ...]]]:
    _, pos = _read_len(buf, 1)
    version, pos = _read_int(buf, pos)
    comm_len, pos = _read_len(buf, pos + 1)
    community = buf[pos : pos + comm_len]
    pos += comm_len
    pdu_type = buf[pos]
    _, pos = _read_len(buf, pos + 1)
    req_id, pos = _read_int(buf, pos)
    _, pos = _read_int(buf, pos)
    _, pos = _read_int(buf, pos)
    vbl_len, pos = _read_len(buf, pos + 1)
    vbl_end = pos + vbl_len
    oids = []
    while pos < vbl_end:
        vb_len, pos = _read_len(buf, pos + 1)
        vb_end = pos + vb_len
        oid, _ = _read_oid(buf, pos)
        oids.append(oid)
        pos = vb_end
    return version, community, pdu_type, req_id, oids


class _MockSnmpUdpServer:
    def __init__(self, handler):
        self._handler = handler
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind(("127.0.0.1", 0))
        self._sock.settimeout(0.05)
        self.endpoint = f"127.0.0.1:{self._sock.getsockname()[1]}"
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self):
        while not self._stop.is_set():
            try:
                data, addr = self._sock.recvfrom(4096)
            except socket.timeout:
                continue
            version, comm, pdu_type, req_id, oids = _decode_request(data)
            varbinds = self._handler(pdu_type, oids)
            vbl = b"".join(_tlv(0x30, _encode_oid(o) + v) for o, v in varbinds)
            pdu = (
                _encode_int(req_id) + _encode_int(0) + _encode_int(0) + _tlv(0x30, vbl)
            )
            pkt = _tlv(0x30, _encode_int(version) + _tlv(0x04, comm) + _tlv(0xA2, pdu))
            self._sock.sendto(pkt, addr)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self._stop.set()
        self._thread.join(timeout=1.0)
        self._sock.close()


def _is_test_snmpd_available() -> bool:
    try:
        snmpdf(["-v", "2c", "-c", "public", "-t", "1", "-r", "0", "localhost:11161"])
        return True
    except (TimeoutError, GenericError):
        return False


def test_top_level_export():
    """Test that snmpdf is exported at the top-level ezsnmp package."""
    assert top_level_snmpdf is snmpdf


def test_invalid_c_option_raises_parse_error():
    """Test that an unknown -C sub-option raises ParseError."""
    with pytest.raises(ParseError):
        snmpdf(["-CZ", "-v", "2c", "-c", "public", "localhost:11161"])


def test_invalid_option_raises_parse_error():
    """Test that an unknown option raises ParseError."""
    with pytest.raises(ParseError):
        snmpdf(["-Z", "-v", "2c", "-c", "public", "localhost:11161"])


def test_help_raises_parse_error():
    """Test that -h raises ParseError."""
    with pytest.raises(ParseError):
        snmpdf(["-h"])


def test_version_raises_parse_error():
    """Test that -V raises ParseError."""
    with pytest.raises(ParseError):
        snmpdf(["-V"])


def test_missing_host_raises_parse_error():
    """Test that empty arguments raise ParseError."""
    with pytest.raises(ParseError):
        snmpdf([])


def test_extra_argument_raises_parse_error():
    """Test that an extra positional argument raises ParseError."""
    with pytest.raises(ParseError):
        snmpdf(["-v", "2c", "-c", "public", "localhost:11161", "extra_arg"])


def test_timeout_raises_timeout_error():
    """Test that an unreachable port raises TimeoutError."""
    with pytest.raises(TimeoutError):
        snmpdf(["-v", "2c", "-c", "public", "-t", "1", "-r", "0", "127.0.0.1:19999"])


def test_invalid_hostname_raises_generic_error():
    """Test that an unresolvable hostname raises GenericError."""
    with pytest.raises(GenericError):
        snmpdf(
            [
                "-v",
                "2c",
                "-c",
                "public",
                "-t",
                "1",
                "-r",
                "0",
                "nonexistent.invalid.host.example:161",
            ]
        )


def test_live_snmpdf_default():
    """Test live snmpdf default output against localhost:11161 when snmpd is running."""
    if not _is_test_snmpd_available():
        pytest.skip("Test snmpd not running on localhost:11161")
    result = snmpdf(["-v", "2c", "-c", "public", "localhost:11161"])
    assert len(result) >= 2
    assert "Description" in result[0]
    assert "Size (kB)" in result[0]
    assert "Used%" in result[0]


def test_live_snmpdf_human_binary():
    """Test live snmpdf -Ch output against localhost:11161 when snmpd is running."""
    if not _is_test_snmpd_available():
        pytest.skip("Test snmpd not running on localhost:11161")
    result = snmpdf(["-Ch", "-v", "2c", "-c", "public", "localhost:11161"])
    assert len(result) >= 2
    assert "Description" in result[0]
    assert "Size" in result[0]
    assert "Size (kB)" not in result[0]


def test_live_snmpdf_human_si():
    """Test live snmpdf -CH output against localhost:11161 when snmpd is running."""
    if not _is_test_snmpd_available():
        pytest.skip("Test snmpd not running on localhost:11161")
    result = snmpdf(["-CH", "-v", "2c", "-c", "public", "localhost:11161"])
    assert len(result) >= 2
    assert "Description" in result[0]
    assert "Size" in result[0]


def test_mock_snmpdf_hr_storage_and_ucd_dsk():
    """Test snmpdf against an in-process loopback UDP responder for hrStorage and -Cu."""
    hr_idx = (1, 3, 6, 1, 2, 1, 25, 2, 3, 1, 1)
    dsk_idx = (1, 3, 6, 1, 4, 1, 2021, 9, 1, 1)

    def handler(pdu_type, oids):
        oid = oids[0]
        if pdu_type == 0xA1:
            if oid == hr_idx:
                return [(hr_idx + (1,), _encode_int(1))]
            if oid == dsk_idx:
                return [(dsk_idx + (1,), _encode_int(1))]
            return [(oid, b"\x82\x00")]
        if len(oids) == 4:
            return [
                (oids[0], _tlv(0x04, b"/")),
                (oids[1], _encode_int(1024)),
                (oids[2], _encode_int(2000)),
                (oids[3], _encode_int(1000)),
            ]
        return [
            (oids[0], _tlv(0x04, b"/dsk")),
            (oids[1], _encode_int(4000)),
            (oids[2], _encode_int(1000)),
        ]

    with _MockSnmpUdpServer(handler) as srv:
        res_default = snmpdf(["-v", "2c", "-c", "public", srv.endpoint])
        assert len(res_default) == 2
        assert "Size (kB)" in res_default[0]
        assert "/" in res_default[1]

        res_ch = snmpdf(["-Ch", "-v", "2c", "-c", "public", srv.endpoint])
        assert "MiB" in res_ch[1]

        res_cu = snmpdf(["-Cu", "-CH", "-v", "2c", "-c", "public", srv.endpoint])
        assert len(res_cu) == 2
        assert "/dsk" in res_cu[1]
        assert "MB" in res_cu[1]


def test_mock_snmpdf_no_partitions_raises_generic_error():
    """Test snmpdf raises GenericError when no partitions are returned."""

    def handler(pdu_type, oids):
        return [(oids[0], b"\x82\x00")]

    with _MockSnmpUdpServer(handler) as srv:
        with pytest.raises(GenericError):
            snmpdf(["-v", "2c", "-c", "public", srv.endpoint])
