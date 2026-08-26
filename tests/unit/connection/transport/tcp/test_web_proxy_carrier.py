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

import pytest

from pyrogram.connection.transport.tcp.web_proxy_carrier import (
    FRAME_HEADER_SIZE,
    FRAME_MAX_PAYLOAD,
    FrameParseError,
    FrameType,
    _HttpConnection,
    derive_bridge_capability,
    parse_frame_message,
    parse_frames,
    serialize_frame,
)
from tests.web_proxy_values import BRIDGE_CAPABILITY_VECTORS

# --- wire frame codec -------------------------------------------------


def test_serialize_parse_round_trip():
    payload = b"hello mtproxy"
    wire = serialize_frame(FrameType.DATA, 42, payload)

    frames, consumed = parse_frames(wire)

    assert consumed == len(wire)
    assert len(frames) == 1
    assert frames[0].type == FrameType.DATA
    assert frames[0].stream_id == 42
    assert frames[0].payload == payload


def test_parse_concatenated_frames():
    a = serialize_frame(FrameType.HELLO, 0, b"\x01")
    b = serialize_frame(FrameType.OPEN, 7, b"")
    c = serialize_frame(FrameType.DATA, 7, b"payload")
    buf = a + b + c

    frames, consumed = parse_frames(buf)

    assert consumed == len(buf)
    assert [f.type for f in frames] == [FrameType.HELLO, FrameType.OPEN, FrameType.DATA]


def test_parse_trailing_partial_frame_not_consumed():
    full = serialize_frame(FrameType.PING, 0, b"")
    partial = bytes([FrameType.DATA, 0, 0, 1, 0, 0, 0])  # header alone, truncated
    buf = full + partial

    frames, consumed = parse_frames(buf)

    assert len(frames) == 1
    assert frames[0].type == FrameType.PING
    assert consumed == len(full)


def test_parse_unknown_type_rejected():
    buf = bytes([0x7F, 0, 0, 0, 0, 0, 0, 0])  # unknown type, zero-length payload
    with pytest.raises(FrameParseError):
        parse_frames(buf)


def test_parse_oversized_payload_rejected():
    buf = bytearray(FRAME_HEADER_SIZE)
    buf[0] = FrameType.DATA
    size = FRAME_MAX_PAYLOAD + 1
    buf[4:8] = size.to_bytes(4, "big")
    with pytest.raises(FrameParseError):
        parse_frames(bytes(buf))


def test_parse_message_rejects_empty_and_partial():
    with pytest.raises(FrameParseError):
        parse_frame_message(b"")

    full = serialize_frame(FrameType.PONG, 0, b"")
    trailing = full + b"\x01"
    with pytest.raises(FrameParseError):
        parse_frame_message(trailing)

    assert parse_frame_message(full)[0].type == FrameType.PONG


def test_serialize_stream_id_encoding():
    wire = serialize_frame(FrameType.WINDOW, 0x00ABCDEF, b"\x00\x00\x00\x01")
    assert wire[1:4] == b"\xab\xcd\xef"


def test_serialize_rejects_out_of_range_stream_id():
    with pytest.raises(ValueError):
        serialize_frame(FrameType.DATA, 0x01000000, b"")


def test_serialize_rejects_oversized_payload():
    with pytest.raises(ValueError):
        serialize_frame(FrameType.DATA, 1, b"\x00" * (FRAME_MAX_PAYLOAD + 1))


def test_large_legal_batch_is_not_rejected():
    # §7.1: the relay may legally batch up to 2 MiB of small frames into one
    # response. A frame-count cap would make that batch a parse error even
    # though every frame in it is well-formed.
    frames = b"".join(serialize_frame(FrameType.PING, 0, b"") for _ in range(20_000))

    parsed, consumed = parse_frames(frames)

    assert consumed == len(frames)
    assert len(parsed) == 20_000


def test_window_frame_round_trips_as_four_byte_big_endian_delta():
    wire = serialize_frame(FrameType.WINDOW, 1, (256 * 1024).to_bytes(4, "big"))

    frame = parse_frame_message(wire)[0]

    assert frame.type == FrameType.WINDOW
    assert int.from_bytes(frame.payload, "big") == 256 * 1024


# --- bridge capability derivation --------------------------------------


def test_derive_bridge_capability_normative_vectors():
    for host, secret_hex, expected in BRIDGE_CAPABILITY_VECTORS:
        secret = bytes.fromhex(secret_hex)
        assert derive_bridge_capability(host, secret) == expected


def test_derive_bridge_capability_is_sensitive_to_host_and_secret():
    secret = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    a = derive_bridge_capability("proxy.example.com", secret)
    b = derive_bridge_capability("other.example.com", secret)
    assert a != b

    other_secret = bytes.fromhex("0f0e0d0c0b0a09080706050403020100")
    c = derive_bridge_capability("proxy.example.com", other_secret)
    assert a != c


# Proxy config parsing (dict form, string link forms, dd-marker handling,
# secret validation) now lives in pyrogram.connection.proxy.normalize_proxy
# and is covered in tests/unit/connection/test_proxy.py; TCP itself only
# takes an already-normalized Proxy dataclass, covered in
# tests/unit/connection/transport/tcp/test_tcp.py.


# --- HTTP response body framing ---------------------------------------


def _connection_reading(raw: bytes) -> _HttpConnection:
    reader = asyncio.StreamReader()
    reader.feed_data(raw)
    reader.feed_eof()

    connection = _HttpConnection("relay.invalid", 443, ssl_context=None)
    connection._reader = reader

    return connection


async def test_read_body_content_length():
    connection = _connection_reading(b"downlink batch")

    body = await connection._read_body(200, {"content-length": "14"})

    assert body == b"downlink batch"


async def test_read_body_chunked():
    # A reverse proxy re-frames larger downlink batches this way, and reading
    # them as an empty body silently dropped every response above a few KiB.
    connection = _connection_reading(b"5\r\nhello\r\n6\r\n mtprx\r\n0\r\n\r\n")

    body = await connection._read_body(200, {"transfer-encoding": "chunked"})

    assert body == b"hello mtprx"


async def test_read_body_chunked_ignores_extensions_and_trailers():
    raw = b"5;name=value\r\nhello\r\n0\r\nx-checksum: 1\r\n\r\n"
    connection = _connection_reading(raw)

    body = await connection._read_body(200, {"transfer-encoding": "CHUNKED"})

    assert body == b"hello"


async def test_read_body_chunked_leaves_the_connection_at_the_next_response():
    raw = b"5\r\nhello\r\n0\r\n\r\nHTTP/1.1 204 No Content\r\n"
    connection = _connection_reading(raw)

    await connection._read_body(200, {"transfer-encoding": "chunked"})

    assert await connection._reader.readline() == b"HTTP/1.1 204 No Content\r\n"


async def test_read_body_no_content_length_is_rejected():
    connection = _connection_reading(b"")

    with pytest.raises(ConnectionError, match="neither Content-Length nor chunked"):
        await connection._read_body(200, {})


async def test_read_body_204_has_no_body():
    connection = _connection_reading(b"")

    assert await connection._read_body(204, {}) == b""


async def test_read_body_rejects_a_malformed_chunk_size():
    connection = _connection_reading(b"zz\r\n")

    with pytest.raises(ConnectionError, match="malformed chunk size"):
        await connection._read_body(200, {"transfer-encoding": "chunked"})


async def test_read_body_rejects_a_truncated_chunked_body():
    connection = _connection_reading(b"5\r\nhello\r\n")

    with pytest.raises(ConnectionError, match="closed inside a chunked body"):
        await connection._read_body(200, {"transfer-encoding": "chunked"})
