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
import os
import re
import socket
import ssl
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import IntEnum
from typing import ClassVar, Dict, List, NamedTuple, Optional, Tuple, TypedDict, Union
from urllib.parse import parse_qs

from python_socks.async_.asyncio import Proxy

from pyrogram import utils
from pyrogram.crypto import aes

log = logging.getLogger(__name__)


# --- WEB proxy: wire frame codec --------------------------------------
# type:u8 | stream_id:u24 (big-endian) | length:u32 (big-endian) | payload
# Matches tdesktop's web_proxy_frame.cpp and the hosted relay byte for byte.

FRAME_HEADER_SIZE = 8
FRAME_MAX_PAYLOAD = 1024 * 1024
FRAME_MAX_BATCH = 4096


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
        if len(frames) >= FRAME_MAX_BATCH:
            raise FrameParseError("frame: too many frames in one batch")

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


# --- WEB proxy: bridge capability ---------------------------------------

_BRIDGE_CONTEXT_PREFIX = b"tdesktop-web-proxy-bridge-v1\n"


def derive_bridge_capability(hostname: str, secret: bytes) -> str:
    # HMAC-SHA256(secret, "tdesktop-web-proxy-bridge-v1\n" + hostname), base64url, no padding.
    # secret keeps its leading 0xDD marker byte when present - unlike the
    # obfuscated2 key derivation below, which strips it.
    context = _BRIDGE_CONTEXT_PREFIX + hostname.encode("utf-8")
    digest = hmac.new(secret, context, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


# --- WEB proxy: long-poll HTTP carrier ----------------------------------
# The raw byte pipe standing in for a raw TCP socket, talking to the
# hosted relay's /api/v1/session* API. TCP._connect_via_web_proxy layers
# the actual MTProxy obfuscation on top of it.

_CONNECT_TIMEOUT = 10
_REQUEST_TIMEOUT = 10
_LONG_POLL_WAIT = 25
_WELCOME_TIMEOUT = 30
_STREAM_ID = 1


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

        self._session_id: Optional[str] = None
        self._up_seq = 0
        self._down_cursor = 0

        self._recv_queue: "asyncio.Queue[Optional[bytes]]" = asyncio.Queue()
        self._welcome_event = asyncio.Event()
        self._closed = False
        self._fail_exc: Optional[Exception] = None
        self._poll_task: Optional[asyncio.Task] = None

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
        frames = [
            serialize_frame(FrameType.DATA, _STREAM_ID, data[offset:offset + FRAME_MAX_PAYLOAD])
            for offset in range(0, len(data), FRAME_MAX_PAYLOAD)
        ]
        await self._send_frames(frames)

    async def recv(self) -> Optional[bytes]:
        return await self._recv_queue.get()

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True

        if self._poll_task is not None:
            self._poll_task.cancel()
            try:
                await self._poll_task
            except (asyncio.CancelledError, Exception):
                pass

        if self._session_id is not None:
            try:
                await self._up.request("DELETE", f"/api/v1/session/{self._session_id}")
            except Exception as e:
                log.debug("WEB proxy: DELETE session failed during close: %s", e)

        await self._up.close()
        await self._down.close()
        self._recv_queue.put_nowait(None)

    async def _send_frames(self, frames: List[bytes]) -> None:
        body = b"".join(frames)
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

                frames, consumed = parse_frames(body)
                if consumed != len(body):
                    raise FrameParseError("downlink message had a trailing partial frame")

                for one_frame in frames:
                    self._handle_frame(one_frame)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            await self._fail(e if isinstance(e, WebCarrierError) else WebCarrierError(str(e)))

    def _handle_frame(self, one_frame: Frame) -> None:
        if one_frame.stream_id == 0:
            if one_frame.type == FrameType.WELCOME:
                self._welcome_event.set()
            elif one_frame.type == FrameType.PING:
                self._loop.create_task(
                    self._send_frames([serialize_frame(FrameType.PONG, 0, one_frame.payload)])
                )
            elif one_frame.type == FrameType.BYE:
                self._loop.create_task(self._fail(WebCarrierError("relay sent BYE")))
            return

        if one_frame.stream_id != _STREAM_ID:
            return

        if one_frame.type == FrameType.DATA:
            self._recv_queue.put_nowait(one_frame.payload)
        elif one_frame.type == FrameType.CLOSE:
            self._loop.create_task(self._fail(WebCarrierError("relay closed the stream")))
        # WINDOW: uplink is never paced against relay-granted credit today.

    async def _fail(self, exc: Exception) -> None:
        if self._fail_exc is not None:
            return
        self._fail_exc = exc
        self._welcome_event.set()
        self._recv_queue.put_nowait(None)


# --- WEB proxy: MTProxy "obfuscated2" handshake -------------------------
# Secret-mixed AES-256-CTR framing with the DC id embedded - what a direct
# MTProxy client speaks to a stock MTProxy server, and so what the relay's
# locally-configured stock MTProxy expects over the carrier above.

_OBFUSCATED2_RESERVED_PREFIXES = (b"HEAD", b"POST", b"GET ", b"OPTI", b"\xee\xee\xee\xee")

CipherArgs = Tuple[bytes, bytearray, bytearray]  # (key, iv, state) for aes.ctr256_{en,de}crypt


class Obfuscated2Header(NamedTuple):
    header: bytes
    encrypt: CipherArgs
    decrypt: CipherArgs


def build_obfuscated2_header(secret: bytes, dc_id: int, obfuscate_tag: bytes) -> Obfuscated2Header:
    # secret is the bare 16-byte key - callers strip any 0xDD marker first.
    if len(secret) != 16:
        raise ValueError(f"obfuscated2: secret must be exactly 16 bytes, got {len(secret)}")
    if len(obfuscate_tag) != 4:
        raise ValueError("obfuscated2: obfuscate_tag must be exactly 4 bytes")

    while True:
        nonce = bytearray(os.urandom(64))
        if (
            nonce[0] != 0xEF
            and bytes(nonce[:4]) not in _OBFUSCATED2_RESERVED_PREFIXES
            and nonce[4:8] != b"\x00\x00\x00\x00"
        ):
            break

    reversed_tail = bytearray(nonce[55:7:-1])

    encrypt_key = hashlib.sha256(bytes(nonce[8:40]) + secret).digest()
    encrypt_iv = bytearray(nonce[40:56])
    decrypt_key = hashlib.sha256(bytes(reversed_tail[0:32]) + secret).digest()
    decrypt_iv = bytearray(reversed_tail[32:48])

    # (iv, state) are mutated in place by every ctr256_{en,de}crypt call, so
    # these tuples must be reused as-is for the life of the connection.
    encrypt: CipherArgs = (encrypt_key, encrypt_iv, bytearray(1))
    decrypt: CipherArgs = (decrypt_key, decrypt_iv, bytearray(1))

    nonce[56:60] = obfuscate_tag
    nonce[60:62] = dc_id.to_bytes(2, "little", signed=True)
    # Encrypting the full buffer both finalizes the tag/dc_id bytes for the
    # wire and advances the keystream 64 bytes, so the first real send()
    # continues it rather than restarting.
    nonce[56:64] = aes.ctr256_encrypt(bytes(nonce), *encrypt)[56:64]

    return Obfuscated2Header(header=bytes(nonce), encrypt=encrypt, decrypt=decrypt)


class ProxyDict(TypedDict):
    scheme: str
    hostname: str
    port: int
    secret: Optional[str]
    username: Optional[str]
    password: Optional[str]


class TCP:
    TIMEOUT = 10

    # Set by a packet-framing subclass (TCPAbridged, TCPIntermediatePadded)
    # safe to use over a WEB proxy: the 4-byte tag stock MTProxy uses to
    # recognize the framing that follows. None = "no obfuscated2 story".
    OBFUSCATE_TAG: ClassVar[Optional[bytes]] = None

    # proxy={"scheme": "web", "hostname": ..., "secret": ...}, or the link
    # forms tg://webproxy?server=...&secret=... / https://t.me/webproxy?...
    _WEB_PROXY_LINK_RE = re.compile(
        r"(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/webproxy\?|tg://webproxy\?)(.+)"
    )

    def __init__(
        self,
        ipv6: bool = False,
        proxy: Optional[Union[str, ProxyDict]] = None,
        crypto_executor_workers: int = 1,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        dc_id: Optional[int] = None,
    ) -> None:
        self.ipv6 = ipv6
        self.proxy = proxy
        # Needed only for the WEB proxy scheme, which routes by relay
        # hostname rather than DC address and embeds this in its handshake.
        self.dc_id = dc_id

        self.crypto_executor_workers = crypto_executor_workers
        self.crypto_executor = ThreadPoolExecutor(
            max_workers=self.crypto_executor_workers, thread_name_prefix="CryptoWorker"
        )

        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

        self.marker_event = asyncio.Event()
        self.lock = asyncio.Lock()

        if isinstance(loop, asyncio.AbstractEventLoop):
            self.loop = loop
        else:
            self.loop = utils.get_event_loop()

        self._web_hostname: Optional[str] = None
        self._web_secret: Optional[bytes] = None  # bare 16 bytes, for obfuscated2
        self._web_full_secret: Optional[bytes] = None  # dd marker kept, for the bridge capability
        self._web_carrier: Optional[WebProxyCarrier] = None
        self._web_recv_buffer = bytearray()
        self._encrypt: Optional[CipherArgs] = None
        self._decrypt: Optional[CipherArgs] = None

        if isinstance(proxy, dict) and proxy.get("scheme", "").lower() == "web":
            self._parse_web_proxy(proxy)
        elif isinstance(proxy, str):
            web_link = self._parse_web_proxy_link(proxy)
            if web_link is not None:
                self._parse_web_proxy(web_link)

    @property
    def is_web_proxy(self) -> bool:
        return self._web_hostname is not None

    @classmethod
    def _parse_web_proxy_link(cls, link: str) -> Optional[dict]:
        match = cls._WEB_PROXY_LINK_RE.match(link)
        if not match:
            return None

        params = parse_qs(match.group(1))
        hostname = params.get("server", [None])[0] or params.get("host", [None])[0]
        secret = params.get("secret", [None])[0]

        if not hostname or not secret:
            raise ValueError("WEB proxy link must contain 'server' (or 'host') and 'secret' params")

        return {"scheme": "web", "hostname": hostname, "secret": secret}

    def _parse_web_proxy(self, proxy: dict) -> None:
        hostname = proxy.get("hostname")
        secret_hex = proxy.get("secret")
        if not hostname or not secret_hex:
            raise ValueError("WEB proxy config requires both 'hostname' and 'secret'")

        try:
            full_secret = bytes.fromhex(secret_hex)
        except ValueError as e:
            raise ValueError(f"WEB proxy 'secret' must be a hex string: {e}") from e

        if len(full_secret) == 17 and full_secret[0] == 0xDD:
            bare_secret = full_secret[1:]
        elif len(full_secret) == 16:
            bare_secret = full_secret
        else:
            raise ValueError(
                f"WEB proxy secret must decode to 16 bytes (plain) or 17 bytes "
                f"(dd-prefixed), got {len(full_secret)}"
            )

        self._web_hostname = hostname
        self._web_secret = bare_secret
        self._web_full_secret = full_secret

    async def _connect_via_web_proxy(self) -> None:
        if self.dc_id is None:
            raise ValueError("The WEB proxy scheme requires a dc_id, passed through by Connection")
        if not self.OBFUSCATE_TAG:
            raise ValueError(
                f"{type(self).__name__} has no OBFUSCATE_TAG and cannot be used over a WEB "
                f"proxy; use e.g. TCPAbridged for a plain secret, TCPIntermediatePadded for dd"
            )
        is_dd_secret = len(self._web_full_secret) == 17
        if is_dd_secret and self.OBFUSCATE_TAG != b"\xdd\xdd\xdd\xdd":
            raise ValueError(
                f"dd-prefixed secrets require TCPIntermediatePadded, not {type(self).__name__}"
            )

        log.info("Connecting to WEB proxy relay %s (dc_id=%s)", self._web_hostname, self.dc_id)

        self._web_carrier = WebProxyCarrier(self._web_hostname, self._web_full_secret, loop=self.loop)
        try:
            await self._web_carrier.start()
        except WebCarrierError as e:
            self._web_carrier = None
            raise OSError(str(e)) from e

        built = build_obfuscated2_header(self._web_secret, self.dc_id, self.OBFUSCATE_TAG)
        self._encrypt = built.encrypt
        self._decrypt = built.decrypt

        try:
            await self._web_carrier.send(built.header)
        except WebCarrierError as e:
            raise OSError(str(e)) from e

        log.info("WEB proxy carrier established")

    async def _build_proxy(self) -> Proxy:
        if isinstance(self.proxy, str):
            match = re.match(r"(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/socks\?|tg://socks\?)(.+)", self.proxy)

            if match:
                params = parse_qs(match.group(1))
                server = params.get("server", [None])[0]
                port = params.get("port", [None])[0]
                user = params.get("user", [None])[0]
                password = params.get("pass", [None])[0]

                if not server or not port:
                    raise ValueError(
                        "Telegram proxy link must contain 'server' and 'port' params"
                    )

                if user and password:
                    url = f"socks5://{user}:{password}@{server}:{port}"
                else:
                    url = f"socks5://{server}:{port}"

                return Proxy.from_url(url)

            return Proxy.from_url(self.proxy)

        scheme = self.proxy.get("scheme", "").lower()
        hostname = self.proxy.get("hostname")
        port = self.proxy.get("port")
        username = self.proxy.get("username")
        password = self.proxy.get("password")

        if not scheme or not hostname or not port:
            raise ValueError("Proxy dict must contain 'scheme', 'hostname', and 'port'")

        if username and password:
            url = f"{scheme}://{username}:{password}@{hostname}:{port}"
        else:
            url = f"{scheme}://{hostname}:{port}"

        return Proxy.from_url(url)

    @staticmethod
    def _enable_keepalive(sock: socket.socket) -> None:
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

            if hasattr(socket, "TCP_KEEPIDLE"):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)
            if hasattr(socket, "TCP_KEEPINTVL"):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
            if hasattr(socket, "TCP_KEEPCNT"):
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
        except Exception as e:
            log.debug("Could not configure TCP Keep-Alive: %s %s", type(e).__name__, e)

    async def _connect_via_proxy(self, destination: Tuple[str, int]) -> None:
        dest_host, dest_port = destination
        proxy = await self._build_proxy()

        log.info(
            "Connecting to %s:%s via proxy %s",
            dest_host,
            dest_port,
            self.proxy,
        )

        try:
            sock = await proxy.connect(
                dest_host=dest_host,
                dest_port=dest_port,
                timeout=TCP.TIMEOUT,
            )
        except Exception as e:
            log.error("Proxy connection failed: %s %s", type(e).__name__, e)
            raise

        self._enable_keepalive(sock)

        log.info("Proxy connection established")

        self.reader, self.writer = await asyncio.open_connection(sock=sock)

    async def _connect_via_direct(self, destination: Tuple[str, int]) -> None:
        host, port = destination
        family = socket.AF_INET6 if self.ipv6 else socket.AF_INET

        log.info("Connecting to %s:%s", host, port)

        try:
            self.reader, self.writer = await asyncio.open_connection(
                host=host,
                port=port,
                family=family,
            )

            raw_socket = self.writer.get_extra_info("socket")

            if raw_socket:
                self._enable_keepalive(raw_socket)
        except Exception as e:
            log.error("Connection failed: %s %s", type(e).__name__, e)
            raise

        log.info("Connection established")

    async def _connect(self, destination: Tuple[str, int]) -> None:
        if self.is_web_proxy:
            await self._connect_via_web_proxy()
        elif self.proxy:
            await self._connect_via_proxy(destination)
        else:
            await self._connect_via_direct(destination)

    async def connect(self, address: Tuple[str, int]) -> None:
        try:
            await asyncio.wait_for(self._connect(address), timeout=TCP.TIMEOUT)
        except asyncio.TimeoutError:  # Re-raise as TimeoutError. asyncio.TimeoutError is deprecated in 3.11
            raise TimeoutError("Connection timed out")

    async def close(self) -> None:
        async with self.lock:
            if self._web_carrier is not None:
                carrier, self._web_carrier = self._web_carrier, None
                try:
                    await carrier.close()
                except Exception as e:
                    log.info("WEB proxy close exception: %s %s", type(e).__name__, e)
                return

            if self.writer is None or self.writer.is_closing():
                log.debug("Close called but writer is already None or closing, skipping")
                return None

            try:
                if self.writer.transport is not None:
                    self.writer.transport.abort()

                self.writer.close()
                await asyncio.wait_for(self.writer.wait_closed(), timeout=TCP.TIMEOUT)
            except asyncio.TimeoutError:
                log.warning("Disconnect timed out after %ss", TCP.TIMEOUT)
            except Exception as e:
                log.info("Close exception: %s %s", type(e).__name__, e)
            finally:
                self.writer = None

    async def send(self, data: bytes, wait_for_marker: bool = True) -> None:
        async with self.lock:
            if self._web_carrier is None and (self.writer is None or self.writer.is_closing()):
                log.debug("Send called but writer is None or closing")
                return None

            if wait_for_marker:
                log.debug("Waiting for marker event before sending")
                try:
                    await asyncio.wait_for(self.marker_event.wait(), timeout=TCP.TIMEOUT)
                except asyncio.TimeoutError:
                    log.error("Timed out waiting for marker event after %ss", TCP.TIMEOUT)
                    raise TimeoutError
                log.debug("Marker event received, proceeding with send")

            if self._encrypt is not None:
                data = await self.loop.run_in_executor(
                    self.crypto_executor, aes.ctr256_encrypt, data, *self._encrypt
                )

            log.debug("Sending %d bytes", len(data))
            try:
                if self._web_carrier is not None:
                    await self._web_carrier.send(data)
                else:
                    self.writer.write(data)
                    await self.writer.drain()
                log.debug("Send complete")
            except Exception as e:
                log.error("Send failed: %s %s", type(e).__name__, e)
                raise OSError(e)

    async def recv(self, length: int = 0) -> Optional[bytes]:
        if self._web_carrier is not None:
            data = await self._recv_from_web_proxy(length)
        else:
            data = await self._recv_from_socket(length)

        if data is not None and self._decrypt is not None:
            data = await self.loop.run_in_executor(
                self.crypto_executor, aes.ctr256_decrypt, data, *self._decrypt
            )

        return data

    async def _recv_from_web_proxy(self, length: int) -> Optional[bytes]:
        # Buffers arbitrary-sized carrier chunks into the exact count the caller wants.
        while len(self._web_recv_buffer) < length:
            chunk = await self._web_carrier.recv()
            if chunk is None:
                return None
            self._web_recv_buffer.extend(chunk)

        result = bytes(self._web_recv_buffer[:length])
        del self._web_recv_buffer[:length]
        return result

    async def _recv_from_socket(self, length: int) -> Optional[bytes]:
        if not self.reader:
            log.debug("Recv called but reader is None")
            return None

        log.debug("Receiving %d bytes", length)
        data = b""

        while len(data) < length:
            try:
                chunk = await asyncio.wait_for(
                    self.reader.read(length - len(data)),
                    timeout=TCP.TIMEOUT,
                )
            except asyncio.TimeoutError:
                log.debug(
                    "Recv timed out after %ss (got %d/%d bytes)", TCP.TIMEOUT, len(data), length
                )
                return None
            except OSError as e:
                log.debug("Recv OSError: %s %s", type(e).__name__, e)
                return None
            else:
                if chunk:
                    data += chunk
                    log.debug(
                        "Received chunk: %d bytes (%d/%d total)", len(chunk), len(data), length
                    )
                else:
                    log.debug(
                        "Recv got empty chunk (connection closed?) after %d/%d bytes",
                        len(data),
                        length,
                    )
                    return None

        log.debug("Recv complete: %d bytes", len(data))
        return data
