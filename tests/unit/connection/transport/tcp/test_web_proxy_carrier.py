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
import logging
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
    _DOWNLINK_GRANT_THRESHOLD,
    _HttpConnection,
    _INITIAL_STREAM_WINDOW,
    _STREAM_ID,
    _UPLINK_FRAME_MAX,
    _WINDOW_PAYLOAD_SIZE,
    derive_bridge_capability,
    parse_frame_message,
    parse_frames,
    serialize_frame,
)
from tests.proxy_values import BRIDGE_CAPABILITY_VECTORS


def test_serialize_parse_round_trip() -> None:
    payload = b"hello mtproxy"
    wire = serialize_frame(FrameType.DATA, stream_id=42, payload=payload)

    parsed = parse_frames(wire)

    assert parsed.consumed == len(wire)
    assert len(parsed.frames) == 1

    assert parsed.frames[0].type == FrameType.DATA
    assert parsed.frames[0].stream_id == 42
    assert parsed.frames[0].payload == payload


def test_parse_concatenated_frames() -> None:
    hello = serialize_frame(FrameType.HELLO, stream_id=0, payload=b"\x01")
    open_stream = serialize_frame(FrameType.OPEN, stream_id=7, payload=b"")
    data = serialize_frame(FrameType.DATA, stream_id=7, payload=b"payload")
    wire = hello + open_stream + data

    parsed = parse_frames(wire)

    assert parsed.consumed == len(wire)
    assert [one_frame.type for one_frame in parsed.frames] == [
        FrameType.HELLO,
        FrameType.OPEN,
        FrameType.DATA,
    ]


def test_parse_trailing_partial_frame_not_consumed() -> None:
    full = serialize_frame(FrameType.PING, stream_id=0, payload=b"")
    partial = bytes([FrameType.DATA, 0, 0, 1, 0, 0, 0])  # header alone, truncated
    wire = full + partial

    parsed = parse_frames(wire)

    assert len(parsed.frames) == 1
    assert parsed.frames[0].type == FrameType.PING
    assert parsed.consumed == len(full)


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

    full = serialize_frame(FrameType.PONG, stream_id=0, payload=b"")
    trailing = full + b"\x01"
    with pytest.raises(FrameParseError):
        parse_frame_message(trailing)

    assert parse_frame_message(full)[0].type == FrameType.PONG


def test_serialize_stream_id_encoding() -> None:
    wire = serialize_frame(FrameType.WINDOW, stream_id=0x00ABCDEF, payload=b"\x00\x00\x00\x01")
    assert wire[1:4] == b"\xab\xcd\xef"


def test_serialize_rejects_out_of_range_stream_id() -> None:
    with pytest.raises(ValueError):
        serialize_frame(FrameType.DATA, stream_id=0x01000000, payload=b"")


def test_serialize_rejects_oversized_payload() -> None:
    with pytest.raises(ValueError):
        serialize_frame(FrameType.DATA, stream_id=1, payload=b"\x00" * (FRAME_MAX_PAYLOAD + 1))


def test_large_legal_batch_is_not_rejected() -> None:
    # §7.1: the relay may legally batch up to 2 MiB of small frames into one
    #  response. A frame-count cap would make that batch a parse error even
    #  though every frame in it is well-formed.
    wire = b"".join(serialize_frame(FrameType.PING, stream_id=0, payload=b"") for _ in range(20_000))

    parsed = parse_frames(wire)

    assert parsed.consumed == len(wire)
    assert len(parsed.frames) == 20_000


def test_window_frame_round_trips_as_four_byte_big_endian_delta() -> None:
    wire = serialize_frame(FrameType.WINDOW, stream_id=1, payload=(256 * 1024).to_bytes(4, "big"))

    frame = parse_frame_message(wire)[0]

    assert frame.type == FrameType.WINDOW
    assert int.from_bytes(frame.payload, "big") == 256 * 1024


def test_derive_bridge_capability_normative_vectors() -> None:
    for host, secret_hex, expected in BRIDGE_CAPABILITY_VECTORS:
        secret = bytes.fromhex(secret_hex)
        assert derive_bridge_capability(host, secret=secret) == expected


def test_derive_bridge_capability_is_sensitive_to_host_and_secret() -> None:
    secret = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
    capability = derive_bridge_capability("proxy.example.com", secret=secret)
    other_host_capability = derive_bridge_capability("other.example.com", secret=secret)
    assert capability != other_host_capability

    other_secret = bytes.fromhex("0f0e0d0c0b0a09080706050403020100")
    other_secret_capability = derive_bridge_capability("proxy.example.com", secret=other_secret)
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

    connection = _HttpConnection("relay.invalid", port=443, ssl_context=None)
    connection._reader = reader

    return connection


async def test_read_body_content_length() -> None:
    connection = _connection_reading(b"downlink batch")

    body = await connection._read_body(HTTPStatus.OK, response_headers={"content-length": "14"})

    assert body == b"downlink batch"


async def test_read_body_chunked() -> None:
    # A reverse proxy re-frames larger downlink batches this way, and reading
    #  them as an empty body silently dropped every response above a few KiB.
    connection = _connection_reading(b"5\r\nhello\r\n6\r\n mtprx\r\n0\r\n\r\n")

    body = await connection._read_body(HTTPStatus.OK, response_headers={"transfer-encoding": "chunked"})

    assert body == b"hello mtprx"


async def test_read_body_chunked_ignores_extensions_and_trailers() -> None:
    raw = b"5;name=value\r\nhello\r\n0\r\nx-checksum: 1\r\n\r\n"
    connection = _connection_reading(raw)

    body = await connection._read_body(HTTPStatus.OK, response_headers={"transfer-encoding": "CHUNKED"})

    assert body == b"hello"


async def test_read_body_chunked_leaves_the_connection_at_the_next_response() -> None:
    raw = b"5\r\nhello\r\n0\r\n\r\nHTTP/1.1 204 No Content\r\n"
    connection = _connection_reading(raw)

    await connection._read_body(HTTPStatus.OK, response_headers={"transfer-encoding": "chunked"})

    assert await connection._reader.readline() == b"HTTP/1.1 204 No Content\r\n"


async def test_read_body_no_content_length_is_rejected() -> None:
    connection = _connection_reading(b"")

    with pytest.raises(ConnectionError, match="neither Content-Length nor chunked"):
        await connection._read_body(HTTPStatus.OK, response_headers={})


async def test_read_body_204_has_no_body() -> None:
    connection = _connection_reading(b"")

    assert await connection._read_body(HTTPStatus.NO_CONTENT, response_headers={}) == b""


async def test_read_body_rejects_a_malformed_chunk_size() -> None:
    connection = _connection_reading(b"zz\r\n")

    with pytest.raises(ConnectionError, match="malformed chunk size"):
        await connection._read_body(HTTPStatus.OK, response_headers={"transfer-encoding": "chunked"})


async def test_read_body_rejects_a_truncated_chunked_body() -> None:
    connection = _connection_reading(b"5\r\nhello\r\n")

    with pytest.raises(ConnectionError, match="closed inside a chunked body"):
        await connection._read_body(HTTPStatus.OK, response_headers={"transfer-encoding": "chunked"})


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
    carrier = WebProxyCarrier("relay.invalid", secret=bytes(16))
    carrier._session_id = "test-session"

    return carrier


def _window_grant(amount: int) -> Frame:
    wire = serialize_frame(FrameType.WINDOW, stream_id=_STREAM_ID, payload=amount.to_bytes(4, "big"))
    parsed = parse_frames(wire)

    return parsed.frames[0]


async def _run_until_blocked(sending: "asyncio.Task[None]") -> None:
    # `send()` suspends once it runs out of credit, and waking it after a WINDOW
    #  grant costs three loop iterations below 3.12, where `asyncio.wait_for` ran the
    #  wait in a task of its own, against one on 3.12+, which awaits the coroutine
    #  directly. A single yield left the grant unspent and failed
    #  `test_send_never_puts_more_on_the_wire_than_the_credit_granted` on 3.9-3.11.
    #  Ten is that measured three with room to spare.
    #  https://github.com/python/cpython/blob/0fb18b02c8ad56299d6a2910be0bab8ad601ef24/Lib/asyncio/tasks.py#L509
    for _ in range(10):
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


async def test_recv_joins_relay_frames_into_the_requested_length() -> None:
    carrier = _carrier()
    _UplinkRecorder(carrier)

    for chunk in (b"abc", b"defg", b"hi"):
        carrier._recv_queue.put_nowait(chunk)

    assert await carrier.recv(5) == b"abcde"
    assert await carrier.recv(4) == b"fghi"


async def test_recv_returns_none_when_the_stream_ends_mid_read() -> None:
    carrier = _carrier()
    _UplinkRecorder(carrier)

    carrier._recv_queue.put_nowait(b"abc")
    carrier._recv_queue.put_nowait(None)

    assert await carrier.recv(8) is None


async def test_recv_grants_downlink_credit_once_the_threshold_is_reached() -> None:
    carrier = _carrier()
    recorder = _UplinkRecorder(carrier)
    carrier._recv_queue.put_nowait(b"\x00" * _DOWNLINK_GRANT_THRESHOLD)

    await carrier.recv(_DOWNLINK_GRANT_THRESHOLD)

    assert recorder.payload_sizes == [_WINDOW_PAYLOAD_SIZE]
    assert carrier._pending_grant == 0
    assert carrier._recv_window_remaining == _INITIAL_STREAM_WINDOW + _DOWNLINK_GRANT_THRESHOLD


async def test_recv_holds_a_grant_below_the_threshold() -> None:
    carrier = _carrier()
    recorder = _UplinkRecorder(carrier)
    carrier._recv_queue.put_nowait(b"\x00" * 16)

    await carrier.recv(16)

    assert recorder.frames == []
    assert carrier._pending_grant == 16


async def _run_failing_tracked_task(carrier: WebProxyCarrier) -> None:
    """Track a task that raises, and let its done callbacks run.

    Nothing awaits a tracked task, so an unretrieved exception reaches asyncio's
    "Task exception was never retrieved" handler and prints a full traceback.
    `asyncio.wait` does not retrieve it the way `gather` would, so this leaves
    the task in exactly the state the callback has to handle.
    """

    async def _fails() -> None:
        raise WebCarrierError("uplink rejected: HTTP 409")

    carrier._track_task(_fails())
    task = next(iter(carrier._background_tasks))

    await asyncio.wait({task})
    # The done callbacks run a loop iteration after the task itself finishes.
    await asyncio.sleep(0)

    assert carrier._background_tasks == set(), "a finished task must not stay in the tracking set"


def _carrier_records(caplog: pytest.LogCaptureFixture) -> List[logging.LogRecord]:
    # `caplog` collects at the root, so a report from another logger lands in it too.
    #  On 3.8 the garbage collector reaches a task an earlier test left pending mid-run
    #  and `asyncio` logs "Task was destroyed but it is pending!" at ERROR, which the
    #  comparisons below then read as a line this module emitted.
    return [record for record in caplog.records if record.name == web_proxy_carrier.log.name]


async def test_a_failed_background_task_the_carrier_recorded_is_reported_at_debug(
    caplog: pytest.LogCaptureFixture,
) -> None:
    carrier = _carrier()
    carrier._fail_exc = WebCarrierError("uplink rejected: HTTP 409")

    with caplog.at_level(logging.DEBUG, logger=web_proxy_carrier.log.name):
        await _run_failing_tracked_task(carrier)

    # The next `send()` raises `_fail_exc` at the caller, so this is the second
    #  report of an error that already has an owner.
    assert [(record.levelno, record.getMessage()) for record in _carrier_records(caplog)] == [
        (logging.DEBUG, "WEB proxy: background task failed: uplink rejected: HTTP 409"),
    ]


async def test_a_failed_background_task_nothing_recorded_is_reported_at_error(
    caplog: pytest.LogCaptureFixture,
) -> None:
    carrier = _carrier()

    with caplog.at_level(logging.DEBUG, logger=web_proxy_carrier.log.name):
        await _run_failing_tracked_task(carrier)

    # `_fail_exc` is unset, so no caller will ever be handed this failure and
    #  swallowing it at debug would lose it outright.
    assert [(record.levelno, record.getMessage()) for record in _carrier_records(caplog)] == [
        (
            logging.ERROR,
            "WEB proxy: background task failed with nothing to report it: uplink rejected: HTTP 409",
        ),
    ]


async def test_a_cancelled_background_task_is_not_reported(caplog: pytest.LogCaptureFixture) -> None:
    carrier = _carrier()

    async def _waits() -> None:
        await asyncio.sleep(60)

    with caplog.at_level(logging.DEBUG, logger=web_proxy_carrier.log.name):
        carrier._track_task(_waits())
        task = next(iter(carrier._background_tasks))

        await carrier._cancel_tracked(task)

    assert _carrier_records(caplog) == []


async def test_recv_after_close_does_not_start_a_grant_task() -> None:
    carrier = _carrier()
    # No session left to `DELETE`, so `close()` needs no network.
    carrier._session_id = None
    carrier._recv_buffer.extend(b"leftover")

    await carrier.close()

    assert await carrier.recv(len(b"leftover")) == b"leftover"

    # `close()` walks `_background_tasks` once and returns, so a grant task
    #  started after it is never cancelled: it sleeps on and then posts a WINDOW
    #  frame down an uplink that is already gone.
    assert carrier._pending_grant == 0
    assert carrier._grant_flush_task is None
    assert carrier._background_tasks == set()
