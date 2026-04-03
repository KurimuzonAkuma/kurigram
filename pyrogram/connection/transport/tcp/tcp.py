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
import hashlib
import hmac
import ipaddress
import logging
import os
import socket
import struct
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Tuple, TypedDict, Union

from python_socks import ProxyType
from python_socks.async_.asyncio import Proxy

from pyrogram import utils
from pyrogram.crypto import aes as _aes

log = logging.getLogger(__name__)

_MTPROXY_RESERVED = (b"HEAD", b"POST", b"GET ", b"OPTI", b"\xee" * 4)


# ─── Fake-TLS helpers ────────────────────────────────────────────────────────

def _tls_record(record_type: int, payload: bytes) -> bytes:
    return bytes([record_type]) + b"\x03\x03" + struct.pack("!H", len(payload)) + payload


def _build_client_hello(client_random: bytes, session_id: bytes, domain: str) -> bytes:
    sni_host = domain.encode()
    sni_name = b"\x00" + struct.pack("!H", len(sni_host)) + sni_host
    sni_list = struct.pack("!H", len(sni_name)) + sni_name
    sni_ext  = b"\x00\x00" + struct.pack("!H", len(sni_list)) + sni_list

    ticket_ext = b"\x00\x23\x00\x00"
    ems_ext    = b"\x00\x17\x00\x00"
    extensions = sni_ext + ticket_ext + ems_ext

    cipher_suites = bytes.fromhex("c02bc02cc02fc030009e009fc013c014002f0035000a")

    # Pad to >= 512 bytes handshake payload using TLS padding extension (0x0015)
    current_size   = 2 + 32 + 1 + len(session_id) + 2 + len(cipher_suites) + 2 + 2 + len(extensions)
    handshake_size = 4 + current_size
    needed = max(0, 512 - handshake_size + 1)
    if needed > 0:
        extensions += b"\x00\x15" + struct.pack("!H", needed) + b"\x00" * needed

    client_hello = (
        b"\x03\x03"
        + client_random
        + bytes([len(session_id)]) + session_id
        + struct.pack("!H", len(cipher_suites)) + cipher_suites
        + b"\x01\x00"
        + struct.pack("!H", len(extensions)) + extensions
    )
    handshake = b"\x01" + struct.pack("!I", len(client_hello))[1:] + client_hello
    return bytes([0x16]) + b"\x03\x01" + struct.pack("!H", len(handshake)) + handshake


def _client_hello_with_hmac(domain: str, secret_bytes: bytes) -> Tuple[bytes, bytes, bytes]:
    session_id   = os.urandom(32)
    timestamp_le = struct.pack("<I", int(time.time()) & 0xFFFFFFFF)
    hello_base   = _build_client_hello(b"\x00" * 32, session_id, domain)
    digest       = hmac.new(secret_bytes, hello_base, hashlib.sha256).digest()
    client_random = bytes(digest[:28]) + bytes(
        a ^ b for a, b in zip(timestamp_le, digest[28:32])
    )
    hello = _build_client_hello(client_random, session_id, domain)
    return hello, client_random, session_id


async def _read_tls_records_until_handshake_done(
    reader: asyncio.StreamReader, timeout: float
) -> None:
    """Consume TLS records until after ChangeCipherSpec + the following fake-cert record."""
    saw_change_cipher = False
    while True:
        try:
            header = await asyncio.wait_for(reader.readexactly(5), timeout=timeout)
        except (asyncio.TimeoutError, asyncio.IncompleteReadError):
            raise ConnectionError("Timeout/disconnect reading server TLS handshake")

        record_type = header[0]
        record_len  = struct.unpack("!H", header[3:5])[0]

        try:
            await asyncio.wait_for(reader.readexactly(record_len), timeout=timeout)
        except (asyncio.TimeoutError, asyncio.IncompleteReadError):
            raise ConnectionError("Timeout/disconnect reading TLS record payload")

        if saw_change_cipher:
            break  # consumed fake-cert after CCS — done
        if record_type == 0x14:
            saw_change_cipher = True
        elif record_type not in (0x16, 0x17):
            raise ConnectionError(f"Unexpected TLS record type {record_type:#04x}")


# ─────────────────────────────────────────────────────────────────────────────


class ProxyDict(TypedDict):
    scheme: str
    hostname: str
    port: int
    username: Optional[str]
    password: Optional[str]
    secret: Optional[str]  # MTProxy only: hex-encoded secret (ee/dd/plain)


class TCP:
    TIMEOUT = 10

    def __init__(
        self,
        ipv6: bool = False,
        proxy: Union[str, ProxyDict, None] = None,
        crypto_executor_workers: int = 1,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        self.ipv6 = ipv6
        self.proxy = proxy

        self.crypto_executor_workers = crypto_executor_workers
        self.crypto_executor = ThreadPoolExecutor(
            max_workers=self.crypto_executor_workers, thread_name_prefix="CryptoWorker"
        )

        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

        self.marker_event = asyncio.Event()
        self.lock = asyncio.Lock()

        self._mtproxy_encrypt: Optional[tuple] = None
        self._mtproxy_decrypt: Optional[tuple] = None
        self._mtproxy_faketls: bool = False
        self._tls_recv_buffer: bytes = b""

        if isinstance(loop, asyncio.AbstractEventLoop):
            self.loop = loop
        else:
            self.loop = utils.get_event_loop()

    async def _build_proxy(self) -> Proxy:
        if isinstance(self.proxy, str):
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
        except Exception as e:
            log.error("Connection failed: %s %s", type(e).__name__, e)
            raise

        log.info("Connection established")

    async def _connect_via_mtproxy(self, destination: Tuple[str, int]) -> None:
        secret_hex = (self.proxy.get("secret") or "").strip().lower()
        if not secret_hex:
            raise ValueError("MTProxy requires a 'secret' field in the proxy dict")

        hostname = self.proxy.get("hostname")
        port     = self.proxy.get("port")

        if secret_hex.startswith("ee"):
            secret_bytes = bytes.fromhex(secret_hex[2:34])
            domain_hex   = secret_hex[34:]
            domain       = bytes.fromhex(domain_hex).decode("utf-8") if domain_hex else None
            await self._connect_via_mtproxy_faketls(secret_bytes, domain, hostname, port)
        elif secret_hex.startswith("dd"):
            secret_bytes = bytes.fromhex(secret_hex[2:])
            if len(secret_bytes) != 16:
                raise ValueError(f"MTProxy dd-secret must be 16 bytes, got {len(secret_bytes)}")
            await self._connect_via_mtproxy_faketls(secret_bytes, None, hostname, port)
        else:
            secret_bytes = bytes.fromhex(secret_hex)
            if len(secret_bytes) != 16:
                raise ValueError(f"MTProxy plain secret must be 16 bytes, got {len(secret_bytes)}")
            await self._connect_via_mtproxy_obf2(secret_bytes, hostname, port)

    async def _connect_via_mtproxy_obf2(
        self, secret_bytes: bytes, hostname: str, port: int
    ) -> None:
        try:
            is_ipv6 = isinstance(ipaddress.ip_address(hostname), ipaddress.IPv6Address)
        except ValueError:
            is_ipv6 = False

        family = socket.AF_INET6 if is_ipv6 else socket.AF_INET
        self.reader, self.writer = await asyncio.open_connection(
            host=hostname, port=port, family=family
        )

        dc_id = self.proxy.get("dc_id", 1)

        while True:
            nonce = bytearray(os.urandom(64))
            if (bytes([nonce[0]]) not in (b"\xef", b"\xdd") and
                    nonce[:4] not in _MTPROXY_RESERVED and
                    nonce[4:8] != b"\x00" * 4):
                nonce[56] = nonce[57] = nonce[58] = nonce[59] = 0xef  # abridged
                nonce[60:62] = struct.pack("<h", dc_id)
                break

        key_part = bytes(nonce[8:40])
        iv_part  = bytes(nonce[40:56])
        enc_key  = hashlib.sha256(key_part + secret_bytes).digest()
        temp     = bytes(nonce[55:7:-1])
        dec_key  = hashlib.sha256(temp[:32] + secret_bytes).digest()

        self._mtproxy_encrypt = (bytearray(enc_key), bytearray(iv_part), bytearray(1))
        self._mtproxy_decrypt = (bytearray(dec_key), bytearray(temp[32:48]), bytearray(1))

        nonce[56:64] = _aes.ctr256_encrypt(bytes(nonce), *self._mtproxy_encrypt)[56:64]
        self.writer.write(bytes(nonce))
        await self.writer.drain()
        log.info("MTProxy obf2 handshake sent to %s:%s", hostname, port)

    async def _connect_via_mtproxy_faketls(
        self, secret_bytes: bytes, domain: Optional[str], hostname: str, port: int
    ) -> None:
        sni_domain = domain or hostname

        try:
            is_ipv6 = isinstance(ipaddress.ip_address(hostname), ipaddress.IPv6Address)
        except ValueError:
            is_ipv6 = False

        family = socket.AF_INET6 if is_ipv6 else socket.AF_INET
        self.reader, self.writer = await asyncio.open_connection(
            host=hostname, port=port, family=family
        )

        client_hello, _, _ = _client_hello_with_hmac(sni_domain, secret_bytes)
        self.writer.write(client_hello)
        await self.writer.drain()

        await _read_tls_records_until_handshake_done(self.reader, TCP.TIMEOUT)

        dc_id = self.proxy.get("dc_id", 1)
        while True:
            nonce = bytearray(os.urandom(64))
            if (bytes([nonce[0]]) not in (b"\xef", b"\xdd") and
                    nonce[:4] not in _MTPROXY_RESERVED and
                    nonce[4:8] != b"\x00" * 4):
                nonce[56] = nonce[57] = nonce[58] = nonce[59] = 0xdd  # padded intermediate
                nonce[60:62] = struct.pack("<h", dc_id)
                break

        key_part = bytes(nonce[8:40])
        iv_part  = bytes(nonce[40:56])
        enc_key  = hashlib.sha256(key_part + secret_bytes).digest()
        temp     = bytes(nonce[55:7:-1])
        dec_key  = hashlib.sha256(temp[:32] + secret_bytes).digest()

        self._mtproxy_encrypt = (bytearray(enc_key), bytearray(iv_part), bytearray(1))
        self._mtproxy_decrypt = (bytearray(dec_key), bytearray(temp[32:48]), bytearray(1))

        nonce[56:64] = _aes.ctr256_encrypt(bytes(nonce), *self._mtproxy_encrypt)[56:64]

        self.writer.write(b"\x14\x03\x03\x00\x01\x01" + _tls_record(0x17, bytes(nonce)))
        await self.writer.drain()
        self._mtproxy_faketls = True
        log.info("MTProxy fake-TLS handshake complete (%s:%s SNI=%s)", hostname, port, sni_domain)

    async def _recv_obf2(self, length: int) -> Optional[bytes]:
        data = b""
        while len(data) < length:
            try:
                chunk = await asyncio.wait_for(
                    self.reader.read(length - len(data)), timeout=TCP.TIMEOUT
                )
            except (OSError, asyncio.TimeoutError):
                return None
            if chunk:
                data += chunk
            else:
                return None
        return _aes.ctr256_decrypt(data, *self._mtproxy_decrypt)

    async def _recv_faketls(self, length: int) -> Optional[bytes]:
        while len(self._tls_recv_buffer) < length:
            try:
                header = await asyncio.wait_for(
                    self.reader.readexactly(5), timeout=TCP.TIMEOUT
                )
            except (asyncio.TimeoutError, asyncio.IncompleteReadError, OSError):
                return None

            record_type = header[0]
            record_len  = struct.unpack("!H", header[3:5])[0]

            try:
                payload = await asyncio.wait_for(
                    self.reader.readexactly(record_len), timeout=TCP.TIMEOUT
                )
            except (asyncio.TimeoutError, asyncio.IncompleteReadError):
                return None

            if record_type != 0x17:
                log.debug("MTProxy fake-TLS: skipping record type %#04x", record_type)
                continue

            self._tls_recv_buffer += _aes.ctr256_decrypt(payload, *self._mtproxy_decrypt)

        data, self._tls_recv_buffer = (
            self._tls_recv_buffer[:length],
            self._tls_recv_buffer[length:],
        )
        return data

    async def _connect(self, destination: Tuple[str, int]) -> None:
        if (isinstance(self.proxy, dict)
                and self.proxy.get("scheme", "").upper() == "MTPROXY"):
            await self._connect_via_mtproxy(destination)
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
            if self.writer is None or self.writer.is_closing():
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

            if self._mtproxy_encrypt is not None:
                data = struct.pack("<I", len(data)) + data
                data = _aes.ctr256_encrypt(data, *self._mtproxy_encrypt)
                if self._mtproxy_faketls:
                    data = _tls_record(0x17, data)

            log.debug("Sending %d bytes", len(data))
            try:
                self.writer.write(data)
                await self.writer.drain()
                log.debug("Send complete")
            except Exception as e:
                log.error("Send failed: %s %s", type(e).__name__, e)
                raise OSError(e)

    async def recv(self, length: int = 0) -> Optional[bytes]:
        if not self.reader:
            log.debug("Recv called but reader is None")
            return None

        if self._mtproxy_encrypt is not None:
            raw = self._recv_faketls if self._mtproxy_faketls else self._recv_obf2
            header = await raw(4)
            if header is None:
                return None
            msg_len = struct.unpack("<I", header)[0]
            result = await raw(msg_len)
            if result:
                # Padded-intermediate framing appends random trailing bytes.
                # Unencrypted MTProto (auth_key_id == 0): strip to 4-byte align.
                # Encrypted MTProto: payload size ≡ 8 mod 16, strip remainder.
                if result[:8] == b"\x00" * 8:
                    trim = len(result) % 4
                else:
                    trim = (len(result) - 8) % 16
                if trim:
                    result = result[:-trim]
            return result

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
