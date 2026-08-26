#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
from http import HTTPStatus
from typing import List

import pytest

from pyrogram.connection.transport.tcp import web_proxy_carrier
from pyrogram.connection.transport.tcp.web_proxy_carrier import (
    FRAME_HEADER_SIZE,
    FRAME_MAX_PAYLOAD,
    Frame,
    FrameParseError,
    FrameType,
    WebCarrierError,
    WebProxyCarrier,
    _HttpConnection,
    _INITIAL_STREAM_WINDOW,
    _STREAM_ID,
    _UPLINK_FRAME_MAX,
    derive_bridge_capability,
    parse_frame_message,
    parse_frames,
    serialize_frame,
)
from tests.web_proxy_values import BRIDGE_CAPABILITY_VECTORS


def test_serialize_parse_round_trip() -> None:
    payload = b"hello mtproxy"
    wire = serialize_frame(FrameType.DATA, 42, payload)

    frames, consumed = parse_frames(wire)

    assert consumed == len(wire)
    assert len(frames) == 1
    assert frames[0].type == FrameType.DATA
    assert frames[0].stream_id == 42
    assert frames[0].payload == payload


def test_parse_concatenated_frames() -> None:
    hello = serialize_frame(FrameType.HELLO, 0, b"\x01")
    open_stream = serialize_frame(FrameType.OPEN, 7, b"")
    data = serialize_frame(FrameType.DATA, 7, b"payload")
    wire = hello + open_stream + data

    frames, consumed = parse_frames(wire)

    assert consumed == len(wire)
    assert [one_frame.type for one_frame in frames] == [FrameType.HELLO, FrameType.OPEN, FrameType.DATA]


def test_parse_trailing_partial_frame_not_consumed() -> None:
    full = serialize_frame(FrameType.PING, 0, b"")
    partial = bytes([FrameType.DATA, 0, 0, 1, 0, 0, 0])  # header alone, truncated
    wire = full + partial

    frames, consumed = parse_frames(wire)

    assert len(frames) == 1
    assert frames[0].type == FrameType.PING
    assert consumed == len(full)


def test_parse_unknown_type_rejected() -> None:
    wire = bytes([0x7F, 0, 0, 0, 0, 0, 0, 0])  # unknown type, zero-length payload
    with pytest.raises(FrameParseError):
        parse_frames(wire)


def test_parse_oversized_payload_rejected() -> None:
    wire = bytearray(FRAME_HEADER_SIZE)
    wire[0] = FrameType.DATA
    oversized = FRAME_MAX_PAYLOAD + 1
    wire[4:8] = oversized.to_bytes(4, "big")

    with pytest.raises(FrameParseError):
        parse_frames(bytes(wire))


def test_parse_message_rejects_empty_and_partial() -> None:
    with pytest.raises(FrameParseError):
        parse_frame_message(b"")

    full = serialize_frame(FrameType.PONG, 0, b"")
    trailing = full + b"\x01"
    with pytest.raises(FrameParseError):
        parse_frame_message(trailing)

    assert parse_frame_message(full)[0].type == FrameType.PONG


def test_serialize_stream_id_encoding() -> None:
    wire = serialize_frame(FrameType.WINDOW, 0x00ABCDEF, b"\x00\x00\x00\x01")
    assert wire[1:4] == b"\xab\xcd\xef"


def test_serialize_rejects_out_of_range_stream_id() -> None:
    with pytest.raises(ValueError):
        serialize_frame(FrameType.DATA, 0x01000000, b"")


def test_serialize_rejects_oversized_payload() -> None:
    with pytest.raises(ValueError):
        serialize_frame(FrameType.DATA, 1, b"\x00" * (FRAME_MAX_PAYLOAD + 1))


def test_large_legal_batch_is_not_rejected() -> None:
    # §7.1: the relay may legally batch up to 2 MiB of small frames into one
    #  response. A frame-count cap would make that batch a parse error even
    #  though every frame in it is well-formed.
    frames = b"".join(serialize_frame(FrameType.PING, 0, b"") for _ in range(20_000))

    parsed, consumed = parse_frames(frames)

    assert consumed == len(frames)
    assert len(parsed) == 20_000


def test_window_frame_round_trips_as_four_byte_big_endian_delta() -> None:
    wire = serialize_frame(FrameType.WINDOW, 1, (256 * 1024).to_bytes(4, "big"))

    frame = parse_frame_message(wire)[0]

    assert frame.type == FrameType.WINDOW
    assert int.from_bytes(frame.payload, "big") == 256 * 1024


def test_derive_bridge_capability_normative_vectors() -> None:
    for host, secret_hex, expected in BRIDGE_CAPABILITY_VECTORS:
        secret = bytes.fromhex(secret_hex)
        assert derive_bridge_capability(host, secret) == expected


def test_derive_bridge_capability_is_sensitive_to_host_and_secret() -> None:
    secret = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    capability = derive_bridge_capability("proxy.example.com", secret)
    other_host_capability = derive_bridge_capability("other.example.com", secret)
    assert capability != other_host_capability

    other_secret = bytes.fromhex("0f0e0d0c0b0a09080706050403020100")
    other_secret_capability = derive_bridge_capability("proxy.example.com", other_secret)
    assert capability != other_secret_capability


# Proxy config parsing (dict form, string link forms, dd-marker handling,
#  secret validation) now lives in pyrogram.connection.proxy.normalize_proxy
#  and is covered in tests/unit/connection/test_proxy.py; TCP itself only
#  takes an already-normalized Proxy dataclass, covered in
#  tests/unit/connection/transport/tcp/test_tcp.py.


def _connection_reading(raw: bytes) -> _HttpConnection:
    reader = asyncio.StreamReader()
    reader.feed_data(raw)
    reader.feed_eof()

    connection = _HttpConnection("relay.invalid", 443, ssl_context=None)
    connection._reader = reader

    return connection


async def test_read_body_content_length() -> None:
    connection = _connection_reading(b"downlink batch")

    body = await connection._read_body(HTTPStatus.OK, {"content-length": "14"})

    assert body == b"downlink batch"


async def test_read_body_chunked() -> None:
    # A reverse proxy re-frames larger downlink batches this way, and reading
    #  them as an empty body silently dropped every response above a few KiB.
    connection = _connection_reading(b"5\r\nhello\r\n6\r\n mtprx\r\n0\r\n\r\n")

    body = await connection._read_body(HTTPStatus.OK, {"transfer-encoding": "chunked"})

    assert body == b"hello mtprx"


async def test_read_body_chunked_ignores_extensions_and_trailers() -> None:
    raw = b"5;name=value\r\nhello\r\n0\r\nx-checksum: 1\r\n\r\n"
    connection = _connection_reading(raw)

    body = await connection._read_body(HTTPStatus.OK, {"transfer-encoding": "CHUNKED"})

    assert body == b"hello"


async def test_read_body_chunked_leaves_the_connection_at_the_next_response() -> None:
    raw = b"5\r\nhello\r\n0\r\n\r\nHTTP/1.1 204 No Content\r\n"
    connection = _connection_reading(raw)

    await connection._read_body(HTTPStatus.OK, {"transfer-encoding": "chunked"})

    assert await connection._reader.readline() == b"HTTP/1.1 204 No Content\r\n"


async def test_read_body_no_content_length_is_rejected() -> None:
    connection = _connection_reading(b"")

    with pytest.raises(ConnectionError, match="neither Content-Length nor chunked"):
        await connection._read_body(HTTPStatus.OK, {})


async def test_read_body_204_has_no_body() -> None:
    connection = _connection_reading(b"")

    assert await connection._read_body(HTTPStatus.NO_CONTENT, {}) == b""


async def test_read_body_rejects_a_malformed_chunk_size() -> None:
    connection = _connection_reading(b"zz\r\n")

    with pytest.raises(ConnectionError, match="malformed chunk size"):
        await connection._read_body(HTTPStatus.OK, {"transfer-encoding": "chunked"})


async def test_read_body_rejects_a_truncated_chunked_body() -> None:
    connection = _connection_reading(b"5\r\nhello\r\n")

    with pytest.raises(ConnectionError, match="closed inside a chunked body"):
        await connection._read_body(HTTPStatus.OK, {"transfer-encoding": "chunked"})


class _UplinkRecorder:
    """Stands in for the relay's uplink endpoint, recording every frame the
    carrier puts on the wire instead of POSTing it."""

    def __init__(self, carrier: WebProxyCarrier) -> None:
        self.frames: List[bytes] = []
        carrier._send_frames = self._record

    async def _record(self, frames: List[bytes]) -> None:
        self.frames.extend(frames)

    @property
    def payload_sizes(self) -> List[int]:
        return [len(one_frame) - FRAME_HEADER_SIZE for one_frame in self.frames]

    @property
    def bytes_sent(self) -> int:
        return sum(self.payload_sizes)


def _carrier() -> WebProxyCarrier:
    carrier = WebProxyCarrier("relay.invalid", bytes(16))
    carrier._session_id = "test-session"

    return carrier


def _window_grant(amount: int) -> Frame:
    wire = serialize_frame(FrameType.WINDOW, _STREAM_ID, amount.to_bytes(4, "big"))
    frames, _consumed = parse_frames(wire)

    return frames[0]


async def _run_until_blocked(sending: "asyncio.Task[None]") -> None:
    # `send()` only suspends once it runs out of credit, so a single loop
    #  iteration is enough to drive it up to that point.
    await asyncio.sleep(0)

    assert not sending.done()


async def test_send_splits_the_payload_at_the_uplink_frame_size() -> None:
    carrier = _carrier()
    recorder = _UplinkRecorder(carrier)
    payload = b"\x00" * (2 * _UPLINK_FRAME_MAX + 100)

    await carrier.send(payload)

    assert recorder.payload_sizes == [_UPLINK_FRAME_MAX, _UPLINK_FRAME_MAX, 100]
    assert carrier._send_window == _INITIAL_STREAM_WINDOW - len(payload)


async def test_send_blocks_once_the_stream_window_is_exhausted() -> None:
    carrier = _carrier()
    recorder = _UplinkRecorder(carrier)
    payload = b"\x00" * (_INITIAL_STREAM_WINDOW + _UPLINK_FRAME_MAX)

    sending = asyncio.ensure_future(carrier.send(payload))
    await _run_until_blocked(sending)

    assert recorder.bytes_sent == _INITIAL_STREAM_WINDOW
    assert carrier._send_window == 0

    carrier._handle_frame(_window_grant(_UPLINK_FRAME_MAX))
    await asyncio.wait_for(sending, timeout=5)

    assert recorder.bytes_sent == len(payload)
    assert carrier._send_window == 0


async def test_send_never_puts_more_on_the_wire_than_the_credit_granted() -> None:
    carrier = _carrier()
    recorder = _UplinkRecorder(carrier)
    payload = b"\x00" * (_INITIAL_STREAM_WINDOW + 3 * _UPLINK_FRAME_MAX)

    sending = asyncio.ensure_future(carrier.send(payload))
    await _run_until_blocked(sending)

    carrier._handle_frame(_window_grant(_UPLINK_FRAME_MAX))
    await _run_until_blocked(sending)

    assert recorder.bytes_sent == _INITIAL_STREAM_WINDOW + _UPLINK_FRAME_MAX

    carrier._handle_frame(_window_grant(2 * _UPLINK_FRAME_MAX))
    await asyncio.wait_for(sending, timeout=5)

    assert recorder.bytes_sent == len(payload)


async def test_send_fails_the_carrier_when_credit_never_arrives(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(web_proxy_carrier, "_CREDIT_WAIT_TIMEOUT", 0.05)
    carrier = _carrier()
    _UplinkRecorder(carrier)
    payload = b"\x00" * (_INITIAL_STREAM_WINDOW + _UPLINK_FRAME_MAX)

    with pytest.raises(WebCarrierError, match="timed out waiting for uplink WINDOW credit"):
        await carrier.send(payload)

    assert carrier._fail_exc is not None


async def test_send_raises_when_the_carrier_fails_while_waiting_for_credit() -> None:
    carrier = _carrier()
    _UplinkRecorder(carrier)
    payload = b"\x00" * (_INITIAL_STREAM_WINDOW + _UPLINK_FRAME_MAX)

    sending = asyncio.ensure_future(carrier.send(payload))
    await _run_until_blocked(sending)

    await carrier._fail(WebCarrierError("relay closed the stream"))

    with pytest.raises(WebCarrierError, match="relay closed the stream"):
        await asyncio.wait_for(sending, timeout=5)
