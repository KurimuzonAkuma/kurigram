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
from http import HTTPStatus
from typing import Coroutine, Dict, Final, FrozenSet, List, Optional, Set

log = logging.getLogger(__name__)


# Section numbers throughout this module refer to tdesktop's WEB proxy plan,
#  which the hosted relay and this carrier both implement.
#  https://github.com/telegramdesktop/tdesktop/blob/23dff657fc857c3223fa20472aa8614b9ab2c7eb/docs/web-proxy-plan.md

# type:u8 | stream_id:u24 (big-endian) | length:u32 (big-endian) | payload, laid
#  out by tdesktop's `SerializeFrame`.
#  https://github.com/telegramdesktop/tdesktop/blob/23dff657fc857c3223fa20472aa8614b9ab2c7eb/Telegram/SourceFiles/mtproto/web_proxy/web_proxy_frame.cpp#L33-L55
FRAME_HEADER_SIZE: Final[int] = 8

# §6: a payload is capped at 1 MiB. Same value as tdesktop's `kMaxFramePayload`.
#  https://github.com/telegramdesktop/tdesktop/blob/23dff657fc857c3223fa20472aa8614b9ab2c7eb/Telegram/SourceFiles/mtproto/web_proxy/web_proxy_frame.h#L18-L35
FRAME_MAX_PAYLOAD: Final[int] = 1024 * 1024


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


_KNOWN_FRAME_TYPES: Final[FrozenSet[int]] = frozenset(frame_type.value for frame_type in FrameType)

# The stream id is three bytes wide.
_MAX_STREAM_ID: Final[int] = 0x00FFFFFF


class FrameParseError(ValueError):
    pass


@dataclass(frozen=True)
class Frame:
    type: FrameType
    stream_id: int
    payload: bytes


def serialize_frame(frame_type: FrameType, *, stream_id: int, payload: bytes) -> bytes:
    if not (0 <= stream_id <= _MAX_STREAM_ID):
        msg = f"frame: stream id {stream_id} out of range"
        raise ValueError(msg)

    if len(payload) > FRAME_MAX_PAYLOAD:
        msg = f"frame: payload too large ({len(payload)} bytes)"
        raise ValueError(msg)

    header = bytes((
        frame_type & 0xFF,
        (stream_id >> 16) & 0xFF,
        (stream_id >> 8) & 0xFF,
        stream_id & 0xFF,
    )) + len(payload).to_bytes(4, "big")

    return header + payload


@dataclass(frozen=True)
class ParsedFrames:
    frames: List[Frame]
    consumed: int  # a trailing partial frame is left unconsumed


def parse_frames(wire: bytes) -> ParsedFrames:
    # No frame-count cap: §7.1 lets the relay batch up to 2 MiB of small frames
    #  into one response, so a count limit would turn a legal batch into a parse
    #  error.
    #  https://github.com/telegramdesktop/tdesktop/blob/23dff657fc857c3223fa20472aa8614b9ab2c7eb/docs/web-proxy-plan.md#L246
    frames: List[Frame] = []
    offset = 0
    wire_len = len(wire)

    while wire_len - offset >= FRAME_HEADER_SIZE:
        type_byte = wire[offset]

        if type_byte not in _KNOWN_FRAME_TYPES:
            msg = f"frame: unknown type 0x{type_byte:02x}"
            raise FrameParseError(msg)

        stream_id = (wire[offset + 1] << 16) | (wire[offset + 2] << 8) | wire[offset + 3]
        size = int.from_bytes(wire[offset + 4:offset + 8], "big")

        if size > FRAME_MAX_PAYLOAD:
            msg = f"frame: payload too large ({size} bytes)"
            raise FrameParseError(msg)

        full = FRAME_HEADER_SIZE + size

        if wire_len - offset < full:
            break

        payload = bytes(wire[offset + FRAME_HEADER_SIZE:offset + full])
        frames.append(Frame(FrameType(type_byte), stream_id, payload))
        offset += full

    return ParsedFrames(frames=frames, consumed=offset)


def parse_frame_message(body: bytes) -> List[Frame]:
    # One HTTP body must be one or more complete frames, nothing more, nothing less.
    if not body:
        msg = "frame: empty message"
        raise FrameParseError(msg)

    parsed = parse_frames(body)

    if parsed.consumed != len(body) or not parsed.frames:
        msg = "frame: trailing partial frame"
        raise FrameParseError(msg)

    return parsed.frames


# §10 defines the derivation below and the vectors the tests check it against.
#  https://github.com/telegramdesktop/tdesktop/blob/23dff657fc857c3223fa20472aa8614b9ab2c7eb/docs/web-proxy-plan.md#L439-L449
_BRIDGE_CONTEXT_PREFIX: Final[bytes] = b"tdesktop-web-proxy-bridge-v1\n"


def derive_bridge_capability(hostname: str, *, secret: bytes) -> str:
    # HMAC-SHA256(secret, "tdesktop-web-proxy-bridge-v1\n" + hostname), base64url, no padding.
    #  secret keeps its leading 0xDD marker byte when present - unlike the
    #  obfuscated2 key derivation, which strips it. hostname must already be
    #  the canonical lowercase ASCII/IDNA form
    #  (`pyrogram.connection.proxy.canonicalize_web_hostname`).
    context = _BRIDGE_CONTEXT_PREFIX + hostname.encode("utf-8")
    digest = hmac.new(secret, context, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


# The raw byte pipe standing in for a TCP socket, talking to the hosted relay's
#  /api/v1/session* API. `TCP._connect_via_web_proxy` layers the actual MTProxy
#  obfuscation on top of it.

_HTTPS_PORT: Final[int] = 443
_CONNECT_TIMEOUT: Final[int] = 10
_REQUEST_TIMEOUT: Final[int] = 10
_LONG_POLL_WAIT: Final[int] = 25
_WELCOME_TIMEOUT: Final[int] = 30

# §6: stream 0 carries the session-wide frames - HELLO, WELCOME, PING, BYE.
#  https://github.com/telegramdesktop/tdesktop/blob/23dff657fc857c3223fa20472aa8614b9ab2c7eb/docs/web-proxy-plan.md#L190
_CONTROL_STREAM_ID: Final[int] = 0

# The carrier is one socket, so it opens exactly one stream and never more.
_STREAM_ID: Final[int] = 1

# §7: "Both directions start with an implicit 4 MiB per-stream window."
#  https://github.com/telegramdesktop/tdesktop/blob/23dff657fc857c3223fa20472aa8614b9ab2c7eb/docs/web-proxy-plan.md#L215
_INITIAL_STREAM_WINDOW: Final[int] = 4 * 1024 * 1024

# §7: the uplink "splits outgoing data into at most 64 KiB frames".
#  https://github.com/telegramdesktop/tdesktop/blob/23dff657fc857c3223fa20472aa8614b9ab2c7eb/docs/web-proxy-plan.md#L226
_UPLINK_FRAME_MAX: Final[int] = 64 * 1024

# §8: downlink credit is granted back coalesced, "once 256 KiB accumulate or
#  after 20 ms".
#  https://github.com/telegramdesktop/tdesktop/blob/23dff657fc857c3223fa20472aa8614b9ab2c7eb/docs/web-proxy-plan.md#L338
_DOWNLINK_GRANT_THRESHOLD: Final[int] = 256 * 1024
_DOWNLINK_GRANT_DELAY: Final[float] = 0.02

# §7: "no write progress for 30 seconds" fails the carrier.
#  https://github.com/telegramdesktop/tdesktop/blob/23dff657fc857c3223fa20472aa8614b9ab2c7eb/docs/web-proxy-plan.md#L237
_CREDIT_WAIT_TIMEOUT: Final[int] = 30


class WebCarrierError(ConnectionError):
    pass


@dataclass(frozen=True)
class StatusAndHeaders:
    status: int
    headers: Dict[str, str]


_CRLF: Final[bytes] = b"\r\n"

# One retry, on a fresh connection - see `_HttpConnection.request`.
_REQUEST_ATTEMPTS: Final[int] = 2

# The relay's HTTP API. §8 names only `DELETE /api/v1/session`, and the relay's
#  own spec describes a different carrier meant for the browser bridge page - a
#  bootstrap token, `POST /api/v1/up`, `X-Up-Seq`. A client with no WebView gets
#  the JSON session API used below instead: `{"bridge": <capability>}` in,
#  `{"id", "cursor"}` back, then `/up?seq=` and `/down?cursor=` under that id.
#  No document describes it, so it was read off a live relay and is what the
#  live tests exercise.
#  https://github.com/telegramdesktop/tdesktop/blob/23dff657fc857c3223fa20472aa8614b9ab2c7eb/docs/web-proxy-plan.md#L343
#  https://github.com/telegramdesktop/tproxy-server/blob/52a5feb7fac38f68da5afef9cedd9b3bfc8473ca/PROTOCOL.md#L193-L216
_SESSION_ENDPOINT: Final[str] = "/api/v1/session"
_CURSOR_HEADER: Final[str] = "x-cursor"
_JSON_CONTENT_TYPE: Final[str] = "application/json"
_FRAMES_CONTENT_TYPE: Final[str] = "application/octet-stream"

# The relay answers the long poll only when it has frames or the wait expires,
#  so the read timeout has to outlast the wait the request itself asks for.
_LONG_POLL_READ_MARGIN: Final[int] = 10

# §6: HELLO carries the one-byte protocol version.
#  https://github.com/telegramdesktop/tdesktop/blob/23dff657fc857c3223fa20472aa8614b9ab2c7eb/docs/web-proxy-plan.md#L190
_HELLO_PAYLOAD: Final[bytes] = b"\x01"

# A WINDOW frame's payload is a big-endian u32 credit count.
_WINDOW_PAYLOAD_SIZE: Final[int] = 4


@dataclass(frozen=True)
class HttpResponse:
    status: int
    headers: Dict[str, str]
    body: bytes


class _HttpConnection:
    # Minimal HTTP/1.1 client for the relay's POST/GET/DELETE calls, over a
    #  single keep-alive connection. Stdlib asyncio/ssl only.

    def __init__(self, host: str, *, port: int, ssl_context: ssl.SSLContext) -> None:
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
                host=self._host,
                port=self._port,
                ssl=self._ssl_context,
                server_hostname=self._host,
            ),
            timeout=_CONNECT_TIMEOUT,
        )

    async def close(self) -> None:
        async with self._lock:
            if self._writer is None:
                return

            try:
                self._writer.close()
                await self._writer.wait_closed()

            except OSError as e:
                log.debug("WEB proxy: closing the HTTP connection failed: %s", e)

            self._writer = None
            self._reader = None

    async def request(
        self,
        method: str,
        *,
        path: str,
        body: bytes = b"",
        headers: Optional[Dict[str, str]] = None,
        timeout: float = _REQUEST_TIMEOUT,
    ) -> HttpResponse:
        last_error: Optional[Exception] = None
        last_detail: str = ""

        # Retries on a fresh connection - the pooled one may have died silently
        #  on the server's idle-keepalive timeout.
        async with self._lock:
            for _attempt in range(_REQUEST_ATTEMPTS):
                try:
                    await self._ensure_connected()

                    return await asyncio.wait_for(
                        self._send_and_read(method, path=path, body=body, headers=headers),
                        timeout=timeout,
                    )

                except (ConnectionError, EOFError, OSError) as e:
                    last_error, last_detail = e, str(e)
                    self._drop_connection()

                # `asyncio.TimeoutError` carries no message of its own.
                except asyncio.TimeoutError as e:
                    last_error, last_detail = e, "timed out"
                    self._drop_connection()

        msg = f"{method} {path}: {last_detail}"
        raise WebCarrierError(msg) from last_error

    def _drop_connection(self) -> None:
        self._writer = None
        self._reader = None

    async def _send_and_read(
        self,
        method: str,
        *,
        path: str,
        body: bytes,
        headers: Optional[Dict[str, str]],
    ) -> HttpResponse:
        request_headers: Dict[str, str] = {
            "Host": self._host,
            "Connection": "keep-alive",
            "Content-Length": str(len(body)),
        }

        if headers:
            request_headers.update(headers)

        lines: List[str] = [f"{method} {path} HTTP/1.1"]
        lines += [f"{name}: {value}" for name, value in request_headers.items()]
        request = ("\r\n".join(lines) + "\r\n\r\n").encode("ascii") + body

        self._writer.write(request)
        await self._writer.drain()

        head = await self._read_status_and_headers()
        response_body = await self._read_body(head.status, response_headers=head.headers)

        # The relay keeps the pool alive, but an intermediary may still ask for
        #  the connection back; the next request then reconnects.
        if head.headers.get("connection", "").lower() == "close":
            self._writer.close()
            self._drop_connection()

        return HttpResponse(status=head.status, headers=head.headers, body=response_body)

    async def _read_body(self, status: int, *, response_headers: Dict[str, str]) -> bytes:
        # A reverse proxy in front of the relay re-frames anything it cannot
        #  buffer whole, so every downlink batch above a few KiB arrives as
        #  `transfer-encoding: chunked` with no `Content-Length`. Reading only
        #  the latter returned an empty body, which `parse_frame_message` then
        #  rejected with "frame: empty message" - the carrier died and every
        #  response larger than about 2 KiB was lost.
        #  https://www.rfc-editor.org/rfc/rfc9112#section-7.1
        transfer_encoding: str = response_headers.get("transfer-encoding", "").lower()

        if "chunked" in transfer_encoding:
            return await self._read_chunked_body()

        content_length_header: Optional[str] = response_headers.get("content-length")

        if content_length_header is not None:
            try:
                content_length = int(content_length_header)

            except ValueError as e:
                msg = f"malformed Content-Length header: {content_length_header!r}"
                raise ConnectionError(msg) from e

            return await self._reader.readexactly(content_length)

        if status == HTTPStatus.NO_CONTENT:
            return b""

        # Anything else would be delimited by the connection closing, which the
        #  relay never does on a keep-alive pool. Treating it as an empty body is
        #  what hid the bug above, so fail loudly instead.
        msg = f"HTTP {status} response has neither Content-Length nor chunked framing"
        raise ConnectionError(msg)

    async def _read_chunked_body(self) -> bytes:
        chunks: List[bytes] = []

        while True:
            size_line: bytes = await self._reader.readline()

            if not size_line:
                msg = "connection closed inside a chunked body"
                raise ConnectionError(msg)

            # The chunk size may carry extensions after a semicolon.
            size_field: bytes = size_line.split(b";", 1)[0].strip()

            try:
                chunk_size = int(size_field, 16)

            except ValueError as e:
                msg = f"malformed chunk size: {size_line!r}"
                raise ConnectionError(msg) from e

            if chunk_size == 0:
                break

            chunks.append(await self._reader.readexactly(chunk_size))

            if await self._reader.readexactly(len(_CRLF)) != _CRLF:
                msg = "malformed chunk terminator"
                raise ConnectionError(msg)

        # Trailer fields, if any, then the blank line closing the body.
        while True:
            line: bytes = await self._reader.readline()

            if line in (_CRLF, b""):
                break

        return b"".join(chunks)

    async def _read_status_and_headers(self) -> StatusAndHeaders:
        status_line: bytes = await self._reader.readline()

        if not status_line:
            msg = "connection closed before a response arrived"
            raise ConnectionError(msg)

        # "HTTP/1.1 204 No Content" - the status code is the second field.
        try:
            status = int(status_line.decode("latin-1").split(None, 2)[1])

        except (IndexError, ValueError) as e:
            msg = f"malformed HTTP status line: {status_line!r}"
            raise ConnectionError(msg) from e

        headers: Dict[str, str] = {}

        while True:
            line: bytes = await self._reader.readline()

            if line in (_CRLF, b""):
                break

            name, _, value = line.decode("latin-1").partition(":")
            headers[name.strip().lower()] = value.strip()

        return StatusAndHeaders(status=status, headers=headers)


class WebProxyCarrier:
    # One relay session, one logical stream (id 1). kurigram opens a fresh
    #  TCP instance per DC/media connection, so - unlike tdesktop, which
    #  multiplexes every account over one process-wide carrier - each gets
    #  its own session; simpler, and keeps failures isolated.

    def __init__(
        self,
        hostname: str,
        *,
        secret: bytes,
        port: int = _HTTPS_PORT,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self._hostname = hostname
        self._secret = secret
        self._loop = loop or asyncio.get_event_loop()

        # `http/1.1` only: the framing this client speaks is HTTP/1.1, and an
        #  ALPN-negotiated h2 would make every response unparseable.
        ssl_context = ssl.create_default_context()
        ssl_context.set_alpn_protocols(["http/1.1"])
        self._ssl_context = ssl_context

        # Uplink and downlink get a connection each: the downlink one is parked
        #  in a long poll almost all the time, and would otherwise block sends.
        self._up = _HttpConnection(hostname, port=port, ssl_context=ssl_context)
        self._down = _HttpConnection(hostname, port=port, ssl_context=ssl_context)
        self._up_send_lock = asyncio.Lock()

        self._session_id: Optional[str] = None
        self._up_seq = 0
        self._down_cursor = 0

        self._send_window = _INITIAL_STREAM_WINDOW
        self._send_window_event = asyncio.Event()
        self._send_window_event.set()

        self._recv_window_remaining = _INITIAL_STREAM_WINDOW
        self._recv_buffer = bytearray()
        self._pending_grant = 0
        self._grant_flush_task: Optional["asyncio.Task"] = None

        self._recv_queue: "asyncio.Queue[Optional[bytes]]" = asyncio.Queue()
        self._welcome_event = asyncio.Event()
        self._closed = False
        self._fail_exc: Optional[Exception] = None
        self._poll_task: Optional["asyncio.Task"] = None
        self._background_tasks: Set["asyncio.Task"] = set()

    async def start(self) -> None:
        # The relay authenticates the session by the bridge capability alone:
        #  proof we hold the secret for this hostname, never the secret itself.
        capability = derive_bridge_capability(self._hostname, secret=self._secret)
        body = json.dumps({"bridge": capability}).encode("utf-8")

        response = await self._up.request(
            "POST",
            path=_SESSION_ENDPOINT,
            body=body,
            headers={"Content-Type": _JSON_CONTENT_TYPE},
        )

        if response.status != HTTPStatus.OK:
            msg = f"session creation rejected: HTTP {response.status}"
            raise WebCarrierError(msg)

        # `{"id": "<session>", "cursor": <int>}`; the cursor is where the
        #  downlink poll starts, and the relay may hand back a non-zero one.
        try:
            session = json.loads(response.body)
            self._session_id = session["id"]
            self._down_cursor = int(session.get("cursor", 0))

        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            msg = f"malformed session creation response: {e}"
            raise WebCarrierError(msg) from e

        # The poll has to be running before HELLO goes out: WELCOME comes back
        #  down the downlink, and nothing would be reading it otherwise.
        self._poll_task = self._loop.create_task(self._poll_loop())

        await self._send_frames([
            serialize_frame(FrameType.HELLO, stream_id=_CONTROL_STREAM_ID, payload=_HELLO_PAYLOAD),
        ])

        try:
            await asyncio.wait_for(self._welcome_event.wait(), timeout=_WELCOME_TIMEOUT)

        except asyncio.TimeoutError:
            exc = WebCarrierError("timed out waiting for WELCOME")
            await self._fail(exc)
            raise exc

        if self._fail_exc is not None:
            raise self._fail_exc

        await self._send_frames([
            serialize_frame(FrameType.OPEN, stream_id=_STREAM_ID, payload=b""),
        ])

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
                # Nothing we are waiting on can arrive until the relay sees what
                #  we already have and grants more credit back - flush before
                #  blocking, not after every chunk is queued.
                if pending:
                    await self._send_frames(pending)
                    pending = []

                await self._spend_send_window(len(chunk))

            else:
                self._send_window -= len(chunk)

            pending.append(serialize_frame(FrameType.DATA, stream_id=_STREAM_ID, payload=chunk))
            offset += len(chunk)

        if pending:
            await self._send_frames(pending)

    async def recv(self, length: int) -> Optional[bytes]:
        # The relay hands over frames of its own choosing, so the buffer is what
        #  turns them into the exact count the caller asked for.
        while len(self._recv_buffer) < length:
            chunk = await self._recv_queue.get()

            if chunk is None:
                return None

            self._recv_buffer.extend(chunk)

        data = bytes(self._recv_buffer[:length])
        del self._recv_buffer[:length]

        await self._grant_credit(length)

        return data

    async def _grant_credit(self, amount: int) -> None:
        # Granted where the bytes leave for the MTProto engine above, which is
        #  the drain point §7 ties downlink credit to - not where they arrive
        #  off the wire.
        if amount <= 0 or self._fail_exc is not None:
            return

        self._pending_grant += amount

        if self._pending_grant >= _DOWNLINK_GRANT_THRESHOLD:
            await self._flush_grant()
            return

        if self._grant_flush_task is None:
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

        # §8: the session is dropped by `DELETE`; a relay that never sees it
        #  keeps the session alive until its own idle timeout expires.
        if self._session_id is not None:
            try:
                await self._up.request("DELETE", path=f"{_SESSION_ENDPOINT}/{self._session_id}")

            except WebCarrierError as e:
                log.debug("WEB proxy: DELETE session failed during close: %s", e)

        await self._up.close()
        await self._down.close()

        # `None` is what `recv()` hands its caller as end-of-stream.
        self._recv_queue.put_nowait(None)

    def _track(self, task: "asyncio.Task") -> None:
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    def _track_task(self, coroutine: "Coroutine[None, None, None]") -> None:
        self._track(self._loop.create_task(coroutine))

    async def _cancel_tracked(self, task: "asyncio.Task") -> None:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        except WebCarrierError as e:
            log.debug("WEB proxy: background task ended during close: %s", e)

        # Cleanup boundary: a bug in one background task must not stop close()
        #  from tearing the rest down.
        except Exception:
            log.exception("WEB proxy: background task crashed during close")

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
        credit = amount.to_bytes(_WINDOW_PAYLOAD_SIZE, "big")

        try:
            await self._send_frames([
                serialize_frame(FrameType.WINDOW, stream_id=_STREAM_ID, payload=credit),
            ])

        # The carrier has already failed, so there is nothing left to credit.
        except WebCarrierError as e:
            log.debug("WEB proxy: dropping a WINDOW grant on a failed carrier: %s", e)

    async def _delayed_grant_flush(self) -> None:
        try:
            await asyncio.sleep(_DOWNLINK_GRANT_DELAY)
            await self._flush_grant()

        finally:
            self._grant_flush_task = None

    async def _send_frames(self, frames: List[bytes]) -> None:
        body = b"".join(frames)

        async with self._up_send_lock:
            # `seq` numbers the uplink posts so the relay can order and
            #  de-duplicate them; it is per session and never reused.
            seq = self._up_seq
            self._up_seq += 1

            try:
                response = await self._up.request(
                    "POST",
                    path=f"{_SESSION_ENDPOINT}/{self._session_id}/up?seq={seq}",
                    body=body,
                    headers={"Content-Type": _FRAMES_CONTENT_TYPE},
                )

            except WebCarrierError as e:
                await self._fail(e)
                raise

            if response.status != HTTPStatus.OK:
                exc = WebCarrierError(f"uplink rejected: HTTP {response.status}")
                await self._fail(exc)
                raise exc

    async def _poll_loop(self) -> None:
        try:
            while True:
                await self._poll_once()

        except asyncio.CancelledError:
            raise

        # `FrameParseError` is a `ValueError`, and so is a malformed `x-cursor`.
        except (WebCarrierError, ValueError) as e:
            log.debug("WEB proxy: poll loop stopped: %s", e)
            await self._fail(e if isinstance(e, WebCarrierError) else WebCarrierError(e))

        # Task boundary: a poll loop that dies silently leaves the carrier alive
        #  and every reader waiting forever.
        except Exception as e:
            log.exception("WEB proxy: poll loop crashed")
            await self._fail(WebCarrierError(e))

    async def _poll_once(self) -> None:
        # The long poll: the relay holds the request open for `wait`
        #  milliseconds and answers early as soon as it has frames for us.
        path = (
            f"{_SESSION_ENDPOINT}/{self._session_id}/down"
            f"?cursor={self._down_cursor}&wait={_LONG_POLL_WAIT * 1000}"
        )

        response = await self._down.request(
            "GET",
            path=path,
            timeout=_LONG_POLL_WAIT + _LONG_POLL_READ_MARGIN,
        )

        # An expired wait comes back empty - poll again from the same cursor.
        if response.status == HTTPStatus.NO_CONTENT:
            return

        if response.status != HTTPStatus.OK:
            msg = f"downlink rejected: HTTP {response.status}"
            raise WebCarrierError(msg)

        # The cursor the next poll resumes from. Without it the relay would
        #  replay the frames this response has just delivered.
        cursor_header = response.headers.get(_CURSOR_HEADER)

        if cursor_header is not None:
            self._down_cursor = int(cursor_header)

        for one_frame in parse_frame_message(response.body):
            self._handle_frame(one_frame)

    def _handle_frame(self, one_frame: Frame) -> None:
        if one_frame.stream_id == _CONTROL_STREAM_ID:
            self._handle_control_frame(one_frame)
            return

        # The carrier opens one stream, so anything else is not ours to read.
        if one_frame.stream_id != _STREAM_ID:
            return

        self._handle_stream_frame(one_frame)

    def _handle_control_frame(self, one_frame: Frame) -> None:
        if one_frame.type == FrameType.WELCOME:
            self._welcome_event.set()
            return

        if one_frame.type == FrameType.PING:
            self._track_task(self._send_frames([
                serialize_frame(
                    FrameType.PONG,
                    stream_id=_CONTROL_STREAM_ID,
                    payload=one_frame.payload,
                ),
            ]))
            return

        if one_frame.type == FrameType.BYE:
            self._track_task(self._fail(WebCarrierError("relay sent BYE")))

    def _handle_stream_frame(self, one_frame: Frame) -> None:
        if one_frame.type == FrameType.DATA:
            self._recv_window_remaining -= len(one_frame.payload)

            if self._recv_window_remaining < 0:
                self._track_task(self._fail(
                    WebCarrierError("relay sent DATA beyond granted receive credit"),
                ))
                return

            self._recv_queue.put_nowait(one_frame.payload)
            return

        if one_frame.type == FrameType.CLOSE:
            self._track_task(self._fail(WebCarrierError("relay closed the stream")))
            return

        if one_frame.type == FrameType.WINDOW:
            if len(one_frame.payload) != _WINDOW_PAYLOAD_SIZE:
                self._track_task(self._fail(WebCarrierError("malformed WINDOW frame")))
                return

            self._send_window += int.from_bytes(one_frame.payload, "big")
            self._send_window_event.set()

    async def _fail(self, exc: Exception) -> None:
        if self._fail_exc is not None:
            return

        self._fail_exc = exc

        # Wake everything that could still be waiting: a failed carrier must
        #  raise at its callers rather than leave them blocked for good.
        self._welcome_event.set()
        self._send_window_event.set()
        self._recv_queue.put_nowait(None)

        if self._poll_task is not None and self._poll_task is not asyncio.current_task():
            self._poll_task.cancel()
