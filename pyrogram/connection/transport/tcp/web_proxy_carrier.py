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
import base64
import hashlib
import hmac
import json
import logging
import ssl
from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List, Optional, Tuple

log = logging.getLogger(__name__)


# --- wire frame codec ----------------------------------------------------
# type:u8 | stream_id:u24 (big-endian) | length:u32 (big-endian) | payload
# Matches tdesktop's web_proxy_frame.cpp and the hosted relay byte for byte.

FRAME_HEADER_SIZE = 8
FRAME_MAX_PAYLOAD = 1024 * 1024  # §6: a payload is capped at 1 MiB


class FrameType(IntEnum):
    OPEN = 0x01
    DATA = 0x02
    CLOSE = 0x03
    WINDOW = 0x04
    PING = 0x05
    PONG = 0x06
    HELLO = 0x10
    WELCOME = 0x11
    AUTH_CHALLENGE = 0x12
    AUTH_RESPONSE = 0x13
    BYE = 0x1F


_KNOWN_FRAME_TYPES = frozenset(t.value for t in FrameType)


class FrameParseError(ValueError):
    pass


@dataclass(frozen=True)
class Frame:
    type: FrameType
    stream_id: int
    payload: bytes


def serialize_frame(frame_type: FrameType, stream_id: int, payload: bytes = b"") -> bytes:
    if not (0 <= stream_id <= 0x00FFFFFF):
        raise ValueError(f"frame: stream id {stream_id} out of range")
    if len(payload) > FRAME_MAX_PAYLOAD:
        raise ValueError(f"frame: payload too large ({len(payload)} bytes)")

    header = bytes((
        frame_type & 0xFF,
        (stream_id >> 16) & 0xFF,
        (stream_id >> 8) & 0xFF,
        stream_id & 0xFF,
    )) + len(payload).to_bytes(4, "big")
    return header + payload


def parse_frames(buf: bytes) -> Tuple[List[Frame], int]:
    # Returns (frames, bytes_consumed); a trailing partial frame is left unconsumed.
    # No frame-count cap: the relay may legally batch up to 2 MiB of small frames
    # (§7.1) into one response, and a count limit would make that a parse error.
    frames: List[Frame] = []
    offset = 0
    buf_len = len(buf)

    while buf_len - offset >= FRAME_HEADER_SIZE:
        type_byte = buf[offset]
        if type_byte not in _KNOWN_FRAME_TYPES:
            raise FrameParseError(f"frame: unknown type 0x{type_byte:02x}")

        stream_id = (buf[offset + 1] << 16) | (buf[offset + 2] << 8) | buf[offset + 3]
        size = int.from_bytes(buf[offset + 4:offset + 8], "big")
        if size > FRAME_MAX_PAYLOAD:
            raise FrameParseError(f"frame: payload too large ({size} bytes)")

        full = FRAME_HEADER_SIZE + size
        if buf_len - offset < full:
            break

        payload = bytes(buf[offset + FRAME_HEADER_SIZE:offset + full])
        frames.append(Frame(FrameType(type_byte), stream_id, payload))
        offset += full

    return frames, offset


def parse_frame_message(body: bytes) -> List[Frame]:
    # One HTTP body must be one or more complete frames, nothing more, nothing less.
    if not body:
        raise FrameParseError("frame: empty message")
    frames, consumed = parse_frames(body)
    if consumed != len(body) or not frames:
        raise FrameParseError("frame: trailing partial frame")
    return frames


# --- bridge capability -----------------------------------------------------

_BRIDGE_CONTEXT_PREFIX = b"tdesktop-web-proxy-bridge-v1\n"


def derive_bridge_capability(hostname: str, secret: bytes) -> str:
    # HMAC-SHA256(secret, "tdesktop-web-proxy-bridge-v1\n" + hostname), base64url, no padding.
    # secret keeps its leading 0xDD marker byte when present - unlike the
    # obfuscated2 key derivation, which strips it. hostname must already be
    # the canonical lowercase ASCII/IDNA form (TCP._canonicalize_web_hostname).
    context = _BRIDGE_CONTEXT_PREFIX + hostname.encode("utf-8")
    digest = hmac.new(secret, context, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


# --- long-poll HTTP carrier ------------------------------------------------
# The raw byte pipe standing in for a raw TCP socket, talking to the hosted
# relay's /api/v1/session* API. TCP._connect_via_web_proxy layers the actual
# MTProxy obfuscation on top of it.

_CONNECT_TIMEOUT = 10
_REQUEST_TIMEOUT = 10
_LONG_POLL_WAIT = 25
_WELCOME_TIMEOUT = 30
_STREAM_ID = 1

# §7: both directions start with an implicit 4 MiB per-stream window.
_INITIAL_STREAM_WINDOW = 4 * 1024 * 1024
# §7: uplink "splits outgoing data into at most 64 KiB frames".
_UPLINK_FRAME_MAX = 64 * 1024
# §7/§8: downlink credit is granted back coalesced, once 256 KiB accumulate
# or 20 ms pass, whichever comes first.
_DOWNLINK_GRANT_THRESHOLD = 256 * 1024
_DOWNLINK_GRANT_DELAY = 0.02
# §7: "no write progress for 30 seconds" fails the carrier.
_CREDIT_WAIT_TIMEOUT = 30


class WebCarrierError(ConnectionError):
    pass


class _HttpConnection:
    # Minimal HTTP/1.1 client for the relay's small POST/GET/DELETE calls
    # (Content-Length bodies only, never chunked). Stdlib asyncio/ssl only.

    def __init__(self, host: str, port: int, ssl_context: ssl.SSLContext) -> None:
        self._host = host
        self._port = port
        self._ssl_context = ssl_context
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._lock = asyncio.Lock()

    async def _ensure_connected(self) -> None:
        if self._writer is not None and not self._writer.is_closing():
            return
        self._reader, self._writer = await asyncio.wait_for(
            asyncio.open_connection(
                host=self._host, port=self._port,
                ssl=self._ssl_context, server_hostname=self._host,
            ),
            timeout=_CONNECT_TIMEOUT,
        )

    async def close(self) -> None:
        async with self._lock:
            if self._writer is not None:
                try:
                    self._writer.close()
                    await self._writer.wait_closed()
                except Exception:
                    pass
                self._writer = None
                self._reader = None

    async def request(
        self, method: str, path: str, body: bytes = b"",
        headers: Optional[Dict[str, str]] = None, timeout: float = _REQUEST_TIMEOUT,
    ) -> Tuple[int, Dict[str, str], bytes]:
        # Retries once on a fresh connection - the pooled one may have died
        # silently on the server's idle-keepalive timeout.
        async with self._lock:
            for attempt in (1, 2):
                try:
                    await self._ensure_connected()
                    return await asyncio.wait_for(
                        self._send_and_read(method, path, body, headers), timeout=timeout,
                    )
                except (ConnectionError, EOFError, OSError) as e:
                    self._writer = None
                    self._reader = None
                    if attempt == 2:
                        raise WebCarrierError(f"{method} {path}: {e}") from e
                except asyncio.TimeoutError as e:
                    self._writer = None
                    self._reader = None
                    if attempt == 2:
                        raise WebCarrierError(f"{method} {path}: timed out") from e
            raise AssertionError("unreachable")

    async def _send_and_read(
        self, method: str, path: str, body: bytes, headers: Optional[Dict[str, str]],
    ) -> Tuple[int, Dict[str, str], bytes]:
        request_headers = {
            "Host": self._host, "Connection": "keep-alive", "Content-Length": str(len(body)),
        }
        if headers:
            request_headers.update(headers)

        lines = [f"{method} {path} HTTP/1.1"] + [f"{k}: {v}" for k, v in request_headers.items()]
        request = ("\r\n".join(lines) + "\r\n\r\n").encode("ascii") + body

        self._writer.write(request)
        await self._writer.drain()

        status, resp_headers = await self._read_status_and_headers()
        content_length_header = resp_headers.get("content-length")
        if content_length_header is None:
            resp_body = b""
        else:
            try:
                content_length = int(content_length_header)
            except ValueError as e:
                raise ConnectionError(f"malformed Content-Length header: {content_length_header!r}") from e
            resp_body = await self._reader.readexactly(content_length)

        if resp_headers.get("connection", "").lower() == "close":
            self._writer.close()
            self._writer = None
            self._reader = None

        return status, resp_headers, resp_body

    async def _read_status_and_headers(self) -> Tuple[int, Dict[str, str]]:
        status_line = await self._reader.readline()
        if not status_line:
            raise ConnectionError("connection closed before a response arrived")
        try:
            status = int(status_line.decode("latin-1").split(None, 2)[1])
        except (IndexError, ValueError) as e:
            raise ConnectionError(f"malformed HTTP status line: {status_line!r}") from e

        headers: Dict[str, str] = {}
        while True:
            line = await self._reader.readline()
            if line in (b"\r\n", b""):
                break
            key, _, value = line.decode("latin-1").partition(":")
            headers[key.strip().lower()] = value.strip()

        return status, headers


class WebProxyCarrier:
    # One relay session, one logical stream (id 1). kurigram opens a fresh
    # TCP instance per DC/media connection, so - unlike tdesktop, which
    # multiplexes every account over one process-wide carrier - each gets
    # its own session; simpler, and keeps failures isolated.

    def __init__(
        self, hostname: str, secret: bytes, *,
        port: int = 443, loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self._hostname = hostname
        self._secret = secret
        self._loop = loop or asyncio.get_event_loop()

        ssl_context = ssl.create_default_context()
        ssl_context.set_alpn_protocols(["http/1.1"])
        self._ssl_context = ssl_context

        self._up = _HttpConnection(hostname, port, ssl_context)
        self._down = _HttpConnection(hostname, port, ssl_context)
        self._up_send_lock = asyncio.Lock()

        self._session_id: Optional[str] = None
        self._up_seq = 0
        self._down_cursor = 0

        self._send_window = _INITIAL_STREAM_WINDOW
        self._send_window_event = asyncio.Event()
        self._send_window_event.set()
        self._recv_window_remaining = _INITIAL_STREAM_WINDOW
        self._pending_grant = 0
        self._grant_flush_task: Optional["asyncio.Task"] = None

        self._recv_queue: "asyncio.Queue[Optional[bytes]]" = asyncio.Queue()
        self._welcome_event = asyncio.Event()
        self._closed = False
        self._fail_exc: Optional[Exception] = None
        self._poll_task: Optional["asyncio.Task"] = None
        self._background_tasks: "set" = set()

    async def start(self) -> None:
        capability = derive_bridge_capability(self._hostname, self._secret)
        body = json.dumps({"bridge": capability}).encode("utf-8")

        status, _headers, resp_body = await self._up.request(
            "POST", "/api/v1/session", body=body, headers={"Content-Type": "application/json"},
        )
        if status != 200:
            raise WebCarrierError(f"session creation rejected: HTTP {status}")

        try:
            data = json.loads(resp_body)
            self._session_id = data["id"]
            self._down_cursor = int(data.get("cursor", 0))
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            raise WebCarrierError(f"malformed session creation response: {e}") from e

        self._poll_task = self._loop.create_task(self._poll_loop())

        await self._send_frames([serialize_frame(FrameType.HELLO, 0, b"\x01")])

        try:
            await asyncio.wait_for(self._welcome_event.wait(), timeout=_WELCOME_TIMEOUT)
        except asyncio.TimeoutError:
            exc = WebCarrierError("timed out waiting for WELCOME")
            await self._fail(exc)
            raise exc

        if self._fail_exc is not None:
            raise self._fail_exc

        await self._send_frames([serialize_frame(FrameType.OPEN, _STREAM_ID, b"")])

    async def send(self, data: bytes) -> None:
        if self._fail_exc is not None:
            raise self._fail_exc
        if not data:
            return

        pending: List[bytes] = []
        offset = 0
        while offset < len(data):
            chunk = data[offset:offset + _UPLINK_FRAME_MAX]
            if self._send_window < len(chunk):
                # Nothing we're waiting on can arrive until the relay sees
                # what we already have and grants more credit back - flush
                # before blocking, not after every chunk is queued.
                if pending:
                    await self._send_frames(pending)
                    pending = []
                await self._spend_send_window(len(chunk))
            else:
                self._send_window -= len(chunk)
            pending.append(serialize_frame(FrameType.DATA, _STREAM_ID, chunk))
            offset += len(chunk)

        if pending:
            await self._send_frames(pending)

    async def recv(self) -> Optional[bytes]:
        return await self._recv_queue.get()

    async def grant_credit(self, amount: int) -> None:
        # Called by TCP._recv_from_web_proxy once bytes are actually handed
        # to the caller - the same "drain into the MTProto engine" point §7
        # ties downlink credit to, not merely arriving off the wire.
        if amount <= 0 or self._fail_exc is not None:
            return
        self._pending_grant += amount
        if self._pending_grant >= _DOWNLINK_GRANT_THRESHOLD:
            await self._flush_grant()
        elif self._grant_flush_task is None:
            task = self._loop.create_task(self._delayed_grant_flush())
            self._grant_flush_task = task
            self._track(task)

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True

        if self._poll_task is not None:
            await self._cancel_tracked(self._poll_task)
        for task in list(self._background_tasks):
            await self._cancel_tracked(task)

        if self._session_id is not None:
            try:
                await self._up.request("DELETE", f"/api/v1/session/{self._session_id}")
            except Exception as e:
                log.debug("WEB proxy: DELETE session failed during close: %s", e)

        await self._up.close()
        await self._down.close()
        self._recv_queue.put_nowait(None)

    def _track(self, task: "asyncio.Task") -> None:
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    async def _cancel_tracked(self, task: "asyncio.Task") -> None:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        except Exception as e:
            log.debug("WEB proxy: background task ended with %s during close: %s", type(e).__name__, e)

    async def _spend_send_window(self, amount: int) -> None:
        while self._send_window < amount:
            if self._fail_exc is not None:
                raise self._fail_exc
            self._send_window_event.clear()
            try:
                await asyncio.wait_for(self._send_window_event.wait(), timeout=_CREDIT_WAIT_TIMEOUT)
            except asyncio.TimeoutError:
                exc = WebCarrierError("timed out waiting for uplink WINDOW credit")
                await self._fail(exc)
                raise exc
        self._send_window -= amount

    async def _flush_grant(self) -> None:
        amount, self._pending_grant = self._pending_grant, 0
        if amount <= 0 or self._fail_exc is not None:
            return
        self._recv_window_remaining += amount
        try:
            await self._send_frames([serialize_frame(FrameType.WINDOW, _STREAM_ID, amount.to_bytes(4, "big"))])
        except WebCarrierError:
            pass  # carrier already failed; nothing left to grant credit to

    async def _delayed_grant_flush(self) -> None:
        try:
            await asyncio.sleep(_DOWNLINK_GRANT_DELAY)
            await self._flush_grant()
        finally:
            self._grant_flush_task = None

    async def _send_frames(self, frames: List[bytes]) -> None:
        body = b"".join(frames)
        async with self._up_send_lock:
            seq = self._up_seq
            self._up_seq += 1
            try:
                status, _headers, _body = await self._up.request(
                    "POST", f"/api/v1/session/{self._session_id}/up?seq={seq}",
                    body=body, headers={"Content-Type": "application/octet-stream"},
                )
            except WebCarrierError as e:
                await self._fail(e)
                raise
            if status != 200:
                exc = WebCarrierError(f"uplink rejected: HTTP {status}")
                await self._fail(exc)
                raise exc

    async def _poll_loop(self) -> None:
        try:
            while True:
                path = (
                    f"/api/v1/session/{self._session_id}/down"
                    f"?cursor={self._down_cursor}&wait={_LONG_POLL_WAIT * 1000}"
                )
                status, headers, body = await self._down.request("GET", path, timeout=_LONG_POLL_WAIT + 10)
                if status == 204:
                    continue
                if status != 200:
                    raise WebCarrierError(f"downlink rejected: HTTP {status}")

                cursor_header = headers.get("x-cursor")
                if cursor_header is not None:
                    self._down_cursor = int(cursor_header)

                for one_frame in parse_frame_message(body):
                    self._handle_frame(one_frame)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            log.exception("WEB proxy: poll loop failed")
            await self._fail(e if isinstance(e, WebCarrierError) else WebCarrierError(str(e)))

    def _handle_frame(self, one_frame: Frame) -> None:
        if one_frame.stream_id == 0:
            if one_frame.type == FrameType.WELCOME:
                self._welcome_event.set()
            elif one_frame.type == FrameType.PING:
                self._track(self._loop.create_task(
                    self._send_frames([serialize_frame(FrameType.PONG, 0, one_frame.payload)])
                ))
            elif one_frame.type == FrameType.BYE:
                self._track(self._loop.create_task(self._fail(WebCarrierError("relay sent BYE"))))
            return

        if one_frame.stream_id != _STREAM_ID:
            return

        if one_frame.type == FrameType.DATA:
            self._recv_window_remaining -= len(one_frame.payload)
            if self._recv_window_remaining < 0:
                self._track(self._loop.create_task(
                    self._fail(WebCarrierError("relay sent DATA beyond granted receive credit"))
                ))
                return
            self._recv_queue.put_nowait(one_frame.payload)
        elif one_frame.type == FrameType.CLOSE:
            self._track(self._loop.create_task(self._fail(WebCarrierError("relay closed the stream"))))
        elif one_frame.type == FrameType.WINDOW:
            if len(one_frame.payload) != 4:
                self._track(self._loop.create_task(self._fail(WebCarrierError("malformed WINDOW frame"))))
                return
            self._send_window += int.from_bytes(one_frame.payload, "big")
            self._send_window_event.set()

    async def _fail(self, exc: Exception) -> None:
        if self._fail_exc is not None:
            return
        self._fail_exc = exc
        self._welcome_event.set()
        self._send_window_event.set()
        self._recv_queue.put_nowait(None)
        if self._poll_task is not None and self._poll_task is not asyncio.current_task():
            self._poll_task.cancel()
