import socket
import threading
import pytest

from ezsnmp import snmpstatus as top_level_snmpstatus
from ezsnmp.exceptions import PacketError, ParseError, TimeoutError
from ezsnmp.netsnmp import snmpstatus


def _encode_len(length: int) -> bytes:
    if length < 0x80:
        return bytes([length])
    if length <= 0xFF:
        return bytes([0x81, length])
    return bytes([0x82, (length >> 8) & 0xFF, length & 0xFF])


def _encode_tlv(tag: int, value: bytes) -> bytes:
    return bytes([tag]) + _encode_len(len(value)) + value


def _encode_int(tag: int, value: int) -> bytes:
    if value == 0:
        raw = b"\x00"
    else:
        tmp = []
        v = value
        while v > 0:
            tmp.append(v & 0xFF)
            v >>= 8
        if tmp[-1] & 0x80:
            tmp.append(0x00)
        raw = bytes(reversed(tmp))
    return _encode_tlv(tag, raw)


def _encode_oid(oid: tuple[int, ...]) -> bytes:
    body = bytearray([oid[0] * 40 + oid[1]])
    for sub in oid[2:]:
        parts = [sub & 0x7F]
        sub >>= 7
        while sub > 0:
            parts.append((sub & 0x7F) | 0x80)
            sub >>= 7
        body.extend(reversed(parts))
    return bytes(body)


def _read_len(data: bytes, pos: int) -> tuple[int, int]:
    b = data[pos]
    pos += 1
    if (b & 0x80) == 0:
        return b, pos
    num_bytes = b & 0x7F
    length = 0
    for _ in range(num_bytes):
        length = (length << 8) | data[pos]
        pos += 1
    return length, pos


def _decode_oid(data: bytes) -> tuple[int, ...]:
    out = [data[0] // 40, data[0] % 40]
    i = 1
    while i < len(data):
        sub = 0
        while i < len(data):
            b = data[i]
            i += 1
            sub = (sub << 7) | (b & 0x7F)
            if (b & 0x80) == 0:
                break
        out.append(sub)
    return tuple(out)


def _parse_request(data: bytes):
    pos = 1  # skip 0x30
    _, pos = _read_len(data, pos)
    pos += 1  # version 0x02
    vlen, pos = _read_len(data, pos)
    version_bytes = data[pos : pos + vlen]
    pos += vlen
    pos += 1  # community 0x04
    clen, pos = _read_len(data, pos)
    community_bytes = data[pos : pos + clen]
    pos += clen
    pdu_tag = data[pos]
    pos += 1
    _, pos = _read_len(data, pos)
    pos += 1  # req_id 0x02
    rlen, pos = _read_len(data, pos)
    req_id_bytes = data[pos : pos + rlen]
    pos += rlen
    for _ in range(2):  # errstat, errindex
        pos += 1
        elen, pos = _read_len(data, pos)
        pos += elen
    pos += 1  # varbind list 0x30
    vbl_len, pos = _read_len(data, pos)
    vbl_end = pos + vbl_len
    oids = []
    while pos < vbl_end:
        pos += 1  # 0x30
        vb_len, pos = _read_len(data, pos)
        vb_end = pos + vb_len
        pos += 1  # 0x06
        olen, pos = _read_len(data, pos)
        oids.append(_decode_oid(data[pos : pos + olen]))
        pos = vb_end
    return version_bytes, community_bytes, pdu_tag, req_id_bytes, oids


def _build_response(
    version_bytes: bytes,
    community_bytes: bytes,
    req_id_bytes: bytes,
    errstat: int,
    errindex: int,
    varbinds: list[tuple[tuple[int, ...], bytes]],
) -> bytes:
    vbl_body = b"".join(
        _encode_tlv(0x30, _encode_tlv(0x06, _encode_oid(oid)) + val_tlv)
        for oid, val_tlv in varbinds
    )
    pdu_body = (
        _encode_tlv(0x02, req_id_bytes)
        + _encode_int(0x02, errstat)
        + _encode_int(0x02, errindex)
        + _encode_tlv(0x30, vbl_body)
    )
    msg_body = (
        _encode_tlv(0x02, version_bytes)
        + _encode_tlv(0x04, community_bytes)
        + _encode_tlv(0xA2, pdu_body)
    )
    return _encode_tlv(0x30, msg_body)


class _MockSnmpStatusServer:
    def __init__(self, if_oper_statuses=(1, 2, 2), get_errstat=0):
        self.if_oper_statuses = list(if_oper_statuses)
        self.get_errstat = get_errstat
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", 0))
        self.sock.settimeout(0.05)
        self.port = self.sock.getsockname()[1]
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def target(self) -> str:
        return f"127.0.0.1:{self.port}"

    def _serve(self):
        while not self._stop.is_set():
            try:
                data, client = self.sock.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                break
            version_b, comm_b, pdu_tag, req_id_b, oids = _parse_request(data)
            if pdu_tag == 0xA0:  # GetRequest
                vbs = []
                for oid in oids:
                    if oid == (1, 3, 6, 1, 2, 1, 1, 1, 0):
                        vbs.append((oid, _encode_tlv(0x04, b"MockPyHost")))
                    elif oid == (1, 3, 6, 1, 2, 1, 1, 3, 0):
                        vbs.append((oid, _encode_int(0x43, 123456)))
                    elif oid == (1, 3, 6, 1, 2, 1, 4, 3, 0):
                        vbs.append((oid, _encode_int(0x41, 42)))
                    elif oid == (1, 3, 6, 1, 2, 1, 4, 10, 0):
                        vbs.append((oid, _encode_int(0x41, 84)))
                    else:
                        vbs.append((oid, _encode_tlv(0x05, b"")))
                resp = _build_response(
                    version_b, comm_b, req_id_b, self.get_errstat, 0, vbs
                )
                self.sock.sendto(resp, client)
            elif pdu_tag == 0xA1:  # GetNextRequest
                vbs = []
                for oid in oids:
                    next_idx = oid[10] + 1 if len(oid) >= 11 else 1
                    if next_idx <= len(self.if_oper_statuses) and len(oid) >= 10:
                        next_oid = oid[:10] + (next_idx,)
                        col = oid[9]
                        if col == 8:
                            val = _encode_int(0x02, self.if_oper_statuses[next_idx - 1])
                        elif col == 11:
                            val = _encode_int(0x41, 10)
                        elif col == 12:
                            val = _encode_int(0x41, 2)
                        elif col == 17:
                            val = _encode_int(0x41, 20)
                        else:
                            val = _encode_int(0x41, 3)
                        vbs.append((next_oid, val))
                    else:
                        vbs.append((oid, _encode_tlv(0x82, b"")))
                resp = _build_response(version_b, comm_b, req_id_b, 0, 0, vbs)
                self.sock.sendto(resp, client)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self._stop.set()
        self._thread.join(timeout=1.0)
        self.sock.close()


def test_top_level_export():
    """Test that snmpstatus is exported at the top-level ezsnmp package."""
    assert top_level_snmpstatus is snmpstatus


def test_help_raises_parse_error():
    """Test that -h raises ParseError."""
    with pytest.raises(ParseError):
        snmpstatus(["-h"])


def test_version_raises_parse_error():
    """Test that -V raises ParseError."""
    with pytest.raises(ParseError):
        snmpstatus(["-V"])


def test_empty_args_raises_parse_error():
    """Test that empty arguments raise ParseError."""
    with pytest.raises(ParseError):
        snmpstatus([])


def test_invalid_option_raises_parse_error():
    """Test that an unknown CLI option raises ParseError."""
    with pytest.raises(ParseError):
        snmpstatus(["-Z", "localhost:11161"])


def test_invalid_c_option_raises_parse_error():
    """Test that an unknown -C sub-option raises ParseError."""
    with pytest.raises(ParseError):
        snmpstatus(["-CX", "-v", "2c", "-c", "public", "localhost:11161"])


def test_timeout_on_unreachable_host():
    """Test that an unreachable host raises TimeoutError."""
    with pytest.raises(TimeoutError):
        snmpstatus(
            ["-v", "2c", "-c", "public", "-t", "1", "-r", "0", "127.0.0.1:19999"]
        )


def test_dont_fix_pdus_option_accepted_before_timeout():
    """Test that -Cf is accepted before reaching TimeoutError on unreachable host."""
    with pytest.raises(TimeoutError):
        snmpstatus(
            ["-Cf", "-v", "2c", "-c", "public", "-t", "1", "-r", "0", "127.0.0.1:19999"]
        )


def test_success_multiple_interfaces_and_down_count():
    """Test successful snmpstatus call with multiple interfaces and down count."""
    with _MockSnmpStatusServer(if_oper_statuses=(1, 2, 2)) as server:
        res = snmpstatus(["-v", "2c", "-c", "public", server.target()])
    assert len(res) == 3
    assert "MockPyHost" in res[0]
    assert "Up:" in res[0]
    assert res[1] == "Interfaces: 3, Recv/Trans packets: 36/69 | IP: 42/84"
    assert res[2] == "2 interfaces are down!"


def test_success_one_down_interface():
    """Test successful snmpstatus call with one down interface."""
    with _MockSnmpStatusServer(if_oper_statuses=(1, 2)) as server:
        res = snmpstatus(["-v", "2c", "-c", "public", server.target()])
    assert len(res) == 3
    assert res[2] == "1 interface is down!"


def test_success_no_down_interfaces():
    """Test successful snmpstatus call with all interfaces up."""
    with _MockSnmpStatusServer(if_oper_statuses=(1,)) as server:
        res = snmpstatus(["-v", "2c", "-c", "public", server.target()])
    assert len(res) == 2
    assert res[1] == "Interfaces: 1, Recv/Trans packets: 12/23 | IP: 42/84"


def test_get_error_raises_packet_error():
    """Test that a GET error response raises PacketError."""
    with _MockSnmpStatusServer(get_errstat=5) as server:
        with pytest.raises(PacketError):
            snmpstatus(["-v", "2c", "-c", "public", server.target()])
