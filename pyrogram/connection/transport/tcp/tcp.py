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
from concurrent.futures import ThreadPoolExecutor
from typing import ClassVar, Dict, Final, NamedTuple, Optional, Tuple

import asyncio
from python_socks import ProxyType
from python_socks.async_.asyncio import Proxy as SocksProxy

from pyrogram import utils
from pyrogram.connection.proxy import HTTPProxy, MTProxy, Proxy, SOCKS4Proxy, SOCKS5Proxy, WebProxy
from pyrogram.connection.transport.tcp.web_proxy_carrier import WebCarrierError, WebProxyCarrier
from pyrogram.crypto import aes
from pyrogram.enums import ProxyScheme

log = logging.getLogger(__name__)


# The obfuscated2 handshake: secret-mixed AES-256-CTR framing with the DC id
#  embedded - what a direct MTProxy client speaks to a stock MTProxy server, and
#  so what the relay's locally-configured stock MTProxy expects over the WEB
#  proxy carrier.

_OBFUSCATED2_RESERVED_PREFIXES: Final[Tuple[bytes, ...]] = (
    b"HEAD",
    b"POST",
    b"GET ",
    b"OPTI",
    b"\xee\xee\xee\xee",
)

# The 4-byte tag written at nonce[56:60], by which stock MTProxy recognizes the
#  packet framing that follows.
ABRIDGED_OBFUSCATE_TAG: Final[bytes] = b"\xef\xef\xef\xef"
INTERMEDIATE_PADDED_OBFUSCATE_TAG: Final[bytes] = b"\xdd\xdd\xdd\xdd"

# The obfuscated2 secret is the bare AES key, and a dd-prefixed one carries a
#  marker byte in front of it.
_OBFUSCATED2_SECRET_SIZE: Final[int] = 16
_DD_SECRET_SIZE: Final[int] = _OBFUSCATED2_SECRET_SIZE + 1

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
    if len(secret) != _OBFUSCATED2_SECRET_SIZE:
        msg = f"obfuscated2: secret must be exactly {_OBFUSCATED2_SECRET_SIZE} bytes, got {len(secret)}"
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
        # Needed only for the WEB proxy scheme, which routes by relay
        #  hostname rather than DC address and embeds this in its handshake.
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
        self._encrypt: Optional[CipherArgs] = None
        self._decrypt: Optional[CipherArgs] = None

    @property
    def is_web_proxy(self) -> bool:
        return isinstance(self.proxy, WebProxy)

    async def _connect_via_web_proxy(self) -> None:
        web_proxy: WebProxy = self.proxy

        if self.dc_id is None:
            msg = "The WEB proxy scheme requires a dc_id, passed through by Connection"
            raise ValueError(msg)

        if not self.OBFUSCATE_TAG:
            msg = (
                f"{type(self).__name__} has no OBFUSCATE_TAG and cannot be used over a WEB "
                f"proxy; use e.g. TCPAbridged for a plain secret, TCPIntermediatePadded for dd"
            )
            raise ValueError(msg)

        is_dd_secret = len(web_proxy.secret) == _DD_SECRET_SIZE

        if is_dd_secret and self.OBFUSCATE_TAG != INTERMEDIATE_PADDED_OBFUSCATE_TAG:
            msg = f"dd-prefixed secrets require TCPIntermediatePadded, not {type(self).__name__}"
            raise ValueError(msg)

        bare_secret = web_proxy.secret[1:] if is_dd_secret else web_proxy.secret

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
            return

        if isinstance(self.proxy, MTProxy):
            msg = "Classic MTProxy (scheme='mtproxy') is not implemented yet."
            raise NotImplementedError(msg)

        if self.proxy is not None:
            await self._connect_via_proxy(destination)
            return

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
            data = await self._web_carrier.recv(length)
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
