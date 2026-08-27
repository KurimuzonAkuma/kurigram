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

import hashlib
import logging
import os
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from typing import ClassVar, Dict, Final, NamedTuple, Optional, Tuple

import asyncio
from python_socks import ProxyType
from python_socks.async_.asyncio import Proxy as SocksProxy

from pyrogram import utils
from pyrogram.connection.proxy import (
    MARKED_SECRET_SIZE,
    OBFUSCATED2_SECRET_SIZE,
    HTTPProxy,
    MTProxy,
    Proxy,
    SOCKS4Proxy,
    SOCKS5Proxy,
    WebProxy,
    uses_random_padding,
)
from pyrogram.connection.transport.tcp.faketls_records import (
    GREETING_RESPONSE_PREFIXES,
    RECORD_LENGTH_SIZE,
    FakeTlsRecords,
)
from pyrogram.connection.transport.tcp.web_proxy_carrier import WebCarrierError, WebProxyCarrier
from pyrogram.crypto import aes, faketls
from pyrogram.enums import ProxyScheme

log = logging.getLogger(__name__)


# The obfuscated2 handshake: secret-mixed AES-256-CTR framing with the DC id
#  embedded - what a direct MTProxy client speaks to a stock MTProxy server, and
#  so what the relay's locally-configured stock MTProxy expects over the WEB
#  proxy carrier.

# The first four bytes a nonce must not open with, read off TDLib's own loop.
#  The two repeated bytes are framing tags and `16 03 01 02` is a TLS
#  ClientHello record; the four verbs are the ones stock MTProxy hands to its
#  HTTP fallback, so a nonce opening with one would be answered as a web request.
#  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/TcpTransport.cpp#L99-L101
#  https://github.com/TelegramMessenger/MTProxy/blob/f36d8af769ffaeac36978d38c2c0f6d1104c2137/net/net-tcp-rpc-ext-server.c#L1065
_OBFUSCATED2_RESERVED_PREFIXES: Final[Tuple[bytes, ...]] = (
    b"HEAD",
    b"POST",
    b"GET ",
    b"OPTI",
    b"\xdd\xdd\xdd\xdd",
    b"\xee\xee\xee\xee",
    b"\x16\x03\x01\x02",
)

# The 4-byte tag written at nonce[56:60], by which stock MTProxy recognizes the
#  packet framing that follows.
ABRIDGED_OBFUSCATE_TAG: Final[bytes] = b"\xef\xef\xef\xef"
INTERMEDIATE_PADDED_OBFUSCATE_TAG: Final[bytes] = b"\xdd\xdd\xdd\xdd"

_OBFUSCATE_TAG_SIZE: Final[int] = 4

CipherArgs = Tuple[bytes, bytearray, bytearray]  # (key, iv, state) for aes.ctr256_{en,de}crypt

# The schemes `python_socks` dials for us, and its name for each.
_PYTHON_SOCKS_TYPES: Final[Dict[ProxyScheme, ProxyType]] = {
    ProxyScheme.SOCKS4: ProxyType.SOCKS4,
    ProxyScheme.SOCKS5: ProxyType.SOCKS5,
    ProxyScheme.HTTP: ProxyType.HTTP,
}


def generate_obfuscated2_nonce(reserved_prefixes: Tuple[bytes, ...] = _OBFUSCATED2_RESERVED_PREFIXES) -> bytearray:
    # Avoids fixed prefixes a firewall could use to fingerprint the stream:
    #  a literal 0xef tag byte, common cleartext protocol prefixes, and an
    #  all-zero field. Shared by TCPAbridgedO's plain obfuscated2 handshake
    #  and build_obfuscated2_header's MTProxy-secret variant below.
    while True:
        nonce = bytearray(os.urandom(64))
        if (
            nonce[0] != 0xEF
            and bytes(nonce[:4]) not in reserved_prefixes
            and nonce[4:8] != b"\x00\x00\x00\x00"
        ):
            return nonce


def finalize_obfuscated2_tag(nonce: bytearray, *, encrypt: CipherArgs) -> bytes:
    # Encrypting the whole 64-byte buffer both puts the tag/dc_id bytes
    #  already written at nonce[56:64] onto the wire in obfuscated form and
    #  advances the keystream exactly 64 bytes, so the first real send()
    #  continues it rather than restarting.
    return aes.ctr256_encrypt(bytes(nonce), *encrypt)[56:64]


class Obfuscated2Header(NamedTuple):
    header: bytes
    encrypt: CipherArgs
    decrypt: CipherArgs


def build_obfuscated2_header(secret: bytes, *, dc_id: int, obfuscate_tag: bytes) -> Obfuscated2Header:
    # secret is the bare key - callers strip any 0xDD marker first.
    if len(secret) != OBFUSCATED2_SECRET_SIZE:
        msg = f"obfuscated2: secret must be exactly {OBFUSCATED2_SECRET_SIZE} bytes, got {len(secret)}"
        raise ValueError(msg)

    if len(obfuscate_tag) != _OBFUSCATE_TAG_SIZE:
        msg = f"obfuscated2: obfuscate_tag must be exactly {_OBFUSCATE_TAG_SIZE} bytes"
        raise ValueError(msg)

    nonce = generate_obfuscated2_nonce()
    reversed_tail = bytearray(nonce[55:7:-1])

    encrypt_key = hashlib.sha256(bytes(nonce[8:40]) + secret).digest()
    encrypt_iv = bytearray(nonce[40:56])
    decrypt_key = hashlib.sha256(bytes(reversed_tail[0:32]) + secret).digest()
    decrypt_iv = bytearray(reversed_tail[32:48])

    # (iv, state) are mutated in place by every ctr256_{en,de}crypt call, so
    #  these tuples must be reused as-is for the life of the connection.
    encrypt: CipherArgs = (encrypt_key, encrypt_iv, bytearray(1))
    decrypt: CipherArgs = (decrypt_key, decrypt_iv, bytearray(1))

    nonce[56:60] = obfuscate_tag
    nonce[60:62] = dc_id.to_bytes(2, "little", signed=True)
    nonce[56:64] = finalize_obfuscated2_tag(nonce, encrypt=encrypt)

    return Obfuscated2Header(header=bytes(nonce), encrypt=encrypt, decrypt=decrypt)


class TCP:
    TIMEOUT = 10

    # Set by a packet-framing subclass (TCPAbridged, TCPIntermediatePadded)
    #  safe to use over a WEB proxy: the 4-byte tag stock MTProxy uses to
    #  recognize the framing that follows. None = "no obfuscated2 story".
    OBFUSCATE_TAG: ClassVar[Optional[bytes]] = None

    def __init__(
        self,
        ipv6: bool = False,
        proxy: Optional[Proxy] = None,
        crypto_executor_workers: int = 1,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        dc_id: Optional[int] = None,
    ) -> None:
        self.ipv6 = ipv6
        self.proxy = proxy
        # Required by every obfuscated2 scheme - classic MTProxy as much as WEB -
        #  because the dc id is one of the fields the obfuscated2 header carries.
        #  Connection passes the already-shifted protocol dc id (media/test
        #  mode folded in), not the bare logical one.
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

        self._web_carrier: Optional[WebProxyCarrier] = None
        self._records: Optional[FakeTlsRecords] = None
        self._encrypt: Optional[CipherArgs] = None
        self._decrypt: Optional[CipherArgs] = None

    @property
    def is_web_proxy(self) -> bool:
        return isinstance(self.proxy, WebProxy)

    @property
    def opens_with_obfuscated2_header(self) -> bool:
        # Both schemes open the stream with a 64-byte obfuscated2 header that
        #  already carries OBFUSCATE_TAG, so a framing subclass must not send the
        #  bare tag on top of it.
        return isinstance(self.proxy, (WebProxy, MTProxy))

    def _obfuscated2_secret(self, secret: bytes) -> bytes:
        # Returns the bare key, and first checks the three things every
        #  obfuscated2 handshake needs from the transport. Shared by both schemes
        #  that speak it, so neither can drift from the other on what it accepts.
        if self.dc_id is None:
            msg = "An obfuscated2 proxy scheme requires a dc_id, passed through by Connection"
            raise ValueError(msg)

        if not self.OBFUSCATE_TAG:
            msg = (
                f"{type(self).__name__} has no OBFUSCATE_TAG and cannot speak obfuscated2; use "
                f"e.g. TCPAbridged for a plain secret, TCPIntermediatePadded for dd"
            )
            raise ValueError(msg)

        # A dd or ee secret asks for random padding, and the padded intermediate
        #  transport is the only one that sends any. `Connection` picks that class
        #  on its own, so reaching this means the transport was built by hand.
        if uses_random_padding(self.proxy) and self.OBFUSCATE_TAG != INTERMEDIATE_PADDED_OBFUSCATE_TAG:
            msg = (
                f"this proxy's secret asks for random padding, which {type(self).__name__} "
                f"does not send; use TCPIntermediatePadded"
            )
            raise ValueError(msg)

        if len(secret) == MARKED_SECRET_SIZE:
            return secret[1:]

        return secret

    async def _connect_via_web_proxy(self) -> None:
        web_proxy: WebProxy = self.proxy

        bare_secret = self._obfuscated2_secret(web_proxy.secret)

        log.info("Connecting to WEB proxy relay %s (dc_id=%s)", web_proxy.hostname, self.dc_id)

        carrier = WebProxyCarrier(
            web_proxy.hostname,
            secret=web_proxy.secret,
            loop=self.loop,
        )
        self._web_carrier = carrier
        try:
            await carrier.start()
        except WebCarrierError as e:
            self._web_carrier = None
            await carrier.close()
            raise OSError(e) from e

        built = build_obfuscated2_header(bare_secret, dc_id=self.dc_id, obfuscate_tag=self.OBFUSCATE_TAG)
        self._encrypt = built.encrypt
        self._decrypt = built.decrypt

        try:
            await carrier.send(built.header)
        except WebCarrierError as e:
            self._web_carrier = None
            await carrier.close()
            raise OSError(e) from e

        log.info("WEB proxy carrier established")

    async def _build_proxy(self) -> SocksProxy:
        # Stays `async` because `SocksProxy.__init__` calls
        #  `asyncio.get_event_loop()`, which raises "There is no current event
        #  loop" outside a running one.
        #  https://github.com/romis2012/python-socks/blob/8794dfc734cc6fb98c61099905a9f8de186719b9/python_socks/async_/asyncio/_proxy.py#L38
        proxy = self.proxy

        if not isinstance(proxy, (SOCKS4Proxy, SOCKS5Proxy, HTTPProxy)):
            msg = f"{type(proxy).__name__} cannot be dialed as a SOCKS/HTTP proxy"
            raise ValueError(msg)

        # Passing the fields rather than a URL: `parse_proxy_url` drops a
        #  username that comes without a password, and `unquote()`s both, so a
        #  credential holding `@`, `:` or `%` does not survive the round trip.
        #  https://github.com/romis2012/python-socks/blob/8794dfc734cc6fb98c61099905a9f8de186719b9/python_socks/_helpers.py#L76-L79
        return SocksProxy(
            proxy_type=_PYTHON_SOCKS_TYPES[proxy.scheme],
            host=proxy.hostname,
            port=proxy.port,
            username=proxy.username,
            password=proxy.password,
        )

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

    async def _connect_via_direct(self, destination: Tuple[str, int], *, family: Optional[int] = None) -> None:
        host, port = destination

        if family is None:
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

    async def _connect_via_mtproxy(self) -> None:
        mtproxy: MTProxy = self.proxy

        bare_secret = self._obfuscated2_secret(mtproxy.secret)

        # The proxy sits at its own address, unrelated to the DC address self.ipv6
        #  was derived from, so let getaddrinfo pick the family it actually has.
        await self._connect_via_direct((mtproxy.hostname, mtproxy.port), family=socket.AF_UNSPEC)

        built = build_obfuscated2_header(bare_secret, dc_id=self.dc_id, obfuscate_tag=self.OBFUSCATE_TAG)

        if mtproxy.sni_hostname is None:
            # Written straight to the socket: self.send() is the framing subclass's
            #  override, and TCP.send() would encrypt the header under the very keys
            #  the header is delivering.
            self.writer.write(built.header)
            await self.writer.drain()
        else:
            await self._greet_fake_tls_proxy(domain=mtproxy.sni_hostname, secret=bare_secret)
            self._records = FakeTlsRecords(self._recv_from_socket, prologue=built.header)

        self._encrypt = built.encrypt
        self._decrypt = built.decrypt

    async def _greet_fake_tls_proxy(self, *, domain: str, secret: bytes) -> None:
        # The local clock, where TDLib uses one corrected against the server: the
        #  correction lives in Session, which does not exist yet at connect time.
        #  A proxy accepts a skew of hours, so this only matters on a broken clock.
        hello = faketls.build_client_hello(domain=domain, secret=secret, unix_time=int(time.time()))

        log.info("Greeting the fake-TLS MTProxy as %s", domain)

        self.writer.write(hello.record)
        await self.writer.drain()

        response = await self._read_greeting_response()

        if not faketls.server_hello_is_authentic(response, secret=secret, client_random=hello.random):
            msg = f"fake-TLS: {domain} answered the greeting without knowing the proxy secret"
            raise OSError(msg)

        log.info("Fake-TLS greeting answered")

    async def _read_greeting_response(self) -> bytes:
        response = bytearray()

        for prefix in GREETING_RESPONSE_PREFIXES:
            head = await self._recv_from_socket(len(prefix) + RECORD_LENGTH_SIZE)

            if head is None or head[: len(prefix)] != prefix:
                msg = "fake-TLS: the greeting was not answered with a ServerHello"
                raise OSError(msg)

            body = await self._recv_from_socket(int.from_bytes(head[-RECORD_LENGTH_SIZE:], "big"))

            if body is None:
                msg = "fake-TLS: the connection closed inside the ServerHello"
                raise OSError(msg)

            response += head + body

        # Hashed exactly as it arrived, both segments together, the way TDLib
        #  hashes the span it consumed.
        #  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/TlsInit.cpp#L636-L644
        return bytes(response)

    async def _connect(self, destination: Tuple[str, int]) -> None:
        if self.is_web_proxy:
            await self._connect_via_web_proxy()
            return

        if isinstance(self.proxy, MTProxy):
            await self._connect_via_mtproxy()
            return

        if self.proxy is not None:
            await self._connect_via_proxy(destination)
            return

        await self._connect_via_direct(destination)

    async def connect(self, address: Tuple[str, int]) -> None:
        # Every step of the WEB handshake is already bounded by the carrier's own
        #  timeouts, and they add up well past `TCP.TIMEOUT`: at 10s the relay
        #  never reaches the WELCOME that `_WELCOME_TIMEOUT` waits 30s for, so
        #  the outer guard can only cut a working handshake short.
        if self.is_web_proxy:
            await self._connect(address)
            return

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
                    if self._records is not None:
                        data = self._records.wrap(data)

                    self.writer.write(data)
                    await self.writer.drain()
                log.debug("Send complete")
            except Exception as e:
                log.error("Send failed: %s %s", type(e).__name__, e)
                raise OSError(e)

    async def recv(self, length: int = 0) -> Optional[bytes]:
        if self._web_carrier is not None:
            data = await self._web_carrier.recv(length)
        elif self._records is not None:
            data = await self._records.recv(length)
        else:
            data = await self._recv_from_socket(length)

        if data is not None and self._decrypt is not None:
            data = await self.loop.run_in_executor(
                self.crypto_executor, aes.ctr256_decrypt, data, *self._decrypt
            )

        return data

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
