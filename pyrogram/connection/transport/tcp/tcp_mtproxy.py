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


import os
import time
import hmac
import random
import struct
import asyncio
import hashlib
import logging

from typing import Optional, Tuple, Union

from pyrogram.crypto import aes, faketls

from .tcp import TCP, ProxyDict
 

log = logging.getLogger(__name__)


# Packet codec classes – each defines an obfuscation tag.

class AbridgedPacketCodec:
    obfuscate_tag = b"\xef\xef\xef\xef"

    @staticmethod
    def encode(data: bytes) -> bytes:
        length = len(data) // 4
        if length <= 126:
            return bytes([length]) + data
        else:
            return b"\x7f" + length.to_bytes(3, "little") + data

    @staticmethod
    def decode(reader) -> bytes:
        raise NotImplementedError


class IntermediatePacketCodec:
    obfuscate_tag = b"\xee\xee\xee\xee"

    @staticmethod
    def encode(data: bytes) -> bytes:
        return len(data).to_bytes(4, "little") + data

    @staticmethod
    def decode(reader) -> bytes:
        raise NotImplementedError


class RandomizedIntermediatePacketCodec:
    obfuscate_tag = b"\xdd\xdd\xdd\xdd"

    @staticmethod
    def encode(data: bytes) -> bytes:
        padding = os.urandom(os.urandom(1)[0] % 4)
        return (len(data) + len(padding)).to_bytes(4, "little") + data + padding

    @staticmethod
    def decode(reader) -> bytes:
        raise NotImplementedError


# Main MTProxy transport class with subclasses for each codec.

class TCPMTProxy(TCP):
    packet_codec = AbridgedPacketCodec   # default
    RESERVED = (b"HEAD", b"POST", b"GET ", b"OPTI", b"\xee" * 4)

    def __init__(
        self,
        dc_id: int,
        ipv6: bool = False,
        proxy: Optional[Union[str, ProxyDict]] = None,
        crypto_executor_workers: int = 1,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        super().__init__(ipv6, proxy, crypto_executor_workers, loop)

        self.dc_id = dc_id
        self.secret = None
        self.secret_mode = "ef" # "ef", "ee", or "dd" – used only for parsing
        self.hostname = None
        self.port = None

        self._faketls = False
        self._sni_hostname = "www.google.com"

        self._recv_buf = bytearray()

        if isinstance(proxy, dict) and proxy.get("scheme", "").lower() == "mtproxy":
            self.hostname = proxy.get("hostname")
            self.port = proxy.get("port")
            raw = proxy.get("secret", "")

            if isinstance(raw, str):
                prefix = raw[:2].lower()
                if prefix == "ee":
                    payload_bytes = bytes.fromhex(raw[2:])
                    self.secret = payload_bytes[:16]
                    domain_bytes = payload_bytes[16:]
                    self.secret_mode = "ee"
                    self._sni_hostname = domain_bytes.decode("utf-8", errors="ignore") or "www.google.com"
                    self._faketls = True
                elif prefix == "dd":
                    self.secret = bytes.fromhex(raw[2:])
                    self.secret_mode = "dd"
                else:
                    self.secret = bytes.fromhex(raw)
            else:
                self.secret = raw

        self.is_mtproxy = bool(self.hostname and self.port and self.secret)

        log.info(
            f"TCPMTProxy initialized (dc={dc_id}, mode={self.secret_mode}, "
            f"faketls={self._faketls}, host={self.hostname}:{self.port}, "
            f"codec={self.packet_codec.__name__})"
        )

    async def connect(self, address: Tuple[str, int]) -> None:
        self.marker_event.clear()

        while True:
            nonce = bytearray(os.urandom(64))
            if (
                nonce[0] not in (0xEF, 0xDD)
                and nonce[:4] not in self.RESERVED
                and nonce[4:8] != b"\x00" * 4
            ):
                break

        temp = bytearray(nonce[55:7:-1])
        encrypt_key = hashlib.sha256(bytes(nonce[8:40]) + self.secret).digest()
        decrypt_key = hashlib.sha256(bytes(temp[:32]) + self.secret).digest()

        self.encrypt = (encrypt_key, bytes(nonce[40:56]), bytearray(1))
        self.decrypt = (decrypt_key, bytes(temp[32:48]), bytearray(1))

        nonce[56:60] = self.packet_codec.obfuscate_tag

        nonce[60:62] = self.dc_id.to_bytes(2, "little", signed=True)
        nonce[62:64] = b"\x00\x00"

        encrypted = aes.ctr256_encrypt(bytes(nonce), *self.encrypt)
        nonce[56:64] = encrypted[56:64]

        await super().connect((self.hostname, self.port))

        if self._faketls:
            await self._send_faketls_handshake(nonce)
        else:
            await super().send(nonce, wait_for_marker=False)

        self.marker_event.set()

    async def _send_faketls_handshake(self, nonce: bytearray) -> None:
        client_hello = faketls.build_fake_tls_client_hello(self._sni_hostname)

        h = hmac.new(self.secret, client_hello, hashlib.sha256).digest()
        timestamp = struct.pack("<I", int(time.time()))
        hmac_result = h[:28] + bytes(a ^ b for a, b in zip(h[28:32], timestamp))

        client_hello = client_hello[:11] + hmac_result + client_hello[43:]
        await super().send(client_hello, wait_for_marker=False)

        sh = await super().recv(5)
        if not sh or len(sh) < 5 or sh[0] != 0x16:
            raise ConnectionError(f"FakeTLS: expected ServerHello (0x16), got {sh.hex() if sh else 'None'}")
        await super().recv(int.from_bytes(sh[3:5], "big"))

        ccs = await super().recv(5)
        if not ccs or len(ccs) < 5:
            raise ConnectionError("FakeTLS: short record after ServerHello")
        if ccs[0] != 0x14:
            raise ConnectionError(
                f"FakeTLS: expected ChangeCipherSpec (0x14), got 0x{ccs[0]:02x} "
                "(camouflage fallback - secret/timestamp rejected or not a FakeTLS proxy)"
            )
        await super().recv(int.from_bytes(ccs[3:5], "big"))

        app = await super().recv(5)
        if not app or len(app) < 5 or app[0] != 0x17:
            raise ConnectionError(f"FakeTLS: expected ApplicationData (0x17), got {app.hex() if app else 'None'}")
        app_len = int.from_bytes(app[3:5], "big")
        if app_len:
            await super().recv(app_len)

        await super().send(
            b"\x14\x03\x03\x00\x01\x01" + self._tls_record(0x17, bytes(nonce)),
            wait_for_marker=False,
        )

    def _tls_record(self, record_type: int, data: bytes) -> bytes:
        return struct.pack("!BHH", record_type, 0x0303, len(data)) + data

    async def send(self, data: bytes, *args) -> None:
        if self.packet_codec is RandomizedIntermediatePacketCodec: # Padded intermediate: random padding added
            padding = os.urandom(random.randint(0, 3))
            payload = struct.pack("<I", len(data) + len(padding)) + data + padding
        elif self.packet_codec is IntermediatePacketCodec: # Pure intermediate: no padding
            payload = struct.pack("<I", len(data)) + data
        else: # Abridged (EF)
            length = len(data) // 4
            payload = (
                bytes([length])
                if length <= 126
                else b"\x7f" + length.to_bytes(3, "little")
            ) + data

        encrypted = await self.loop.run_in_executor(
            self.crypto_executor,
            aes.ctr256_encrypt,
            payload,
            *self.encrypt,
        )

        if self._faketls:
            encrypted = self._tls_record(0x17, encrypted)

        await super().send(encrypted)

    async def recv(self, length: int = 0) -> Optional[bytes]:
        if self.packet_codec is IntermediatePacketCodec:
            return await self._recv_intermediate()
        elif self.packet_codec is RandomizedIntermediatePacketCodec:
            return await self._recv_padded()
        else:
            return await self._recv_abridged()

    async def _recv_tls(self, length: int) -> Optional[bytes]:
        while len(self._recv_buf) < length:
            if self._faketls:
                header = await super().recv(5)
                if not header:
                    return None
                record_type, _, record_len = struct.unpack("!BHH", header)
                if record_type != 0x17:
                    await super().recv(record_len)
                    continue
                body = await super().recv(record_len)
                if not body:
                    return None
                self._recv_buf.extend(body)
            else:
                chunk = await super().recv(length - len(self._recv_buf))
                if not chunk:
                    return None
                self._recv_buf.extend(chunk)

        res = bytes(self._recv_buf[:length])
        self._recv_buf = self._recv_buf[length:]
        return res

    async def _recv_intermediate(self) -> Optional[bytes]:
        raw_len = await self._recv_tls(4)
        if raw_len is None:
            return None

        raw_len = aes.ctr256_decrypt(raw_len, *self.decrypt)
        packet_length = int.from_bytes(raw_len, "little")

        data = await self._recv_tls(packet_length)
        if data is None:
            return None

        return await self.loop.run_in_executor(
            self.crypto_executor,
            aes.ctr256_decrypt,
            data,
            *self.decrypt,
        )

    async def _recv_padded(self) -> Optional[bytes]:
        raw_len = await self._recv_tls(4)
        if raw_len is None:
            return None

        raw_len = aes.ctr256_decrypt(raw_len, *self.decrypt)
        packet_length = int.from_bytes(raw_len, "little")

        data = await self._recv_tls(packet_length)
        if data is None:
            return None

        decrypted = await self.loop.run_in_executor(
            self.crypto_executor,
            aes.ctr256_decrypt,
            data,
            *self.decrypt,
        )

        if len(decrypted) >= 20 and decrypted[:8] == b"\x00" * 8:
            real = 20 + int.from_bytes(decrypted[16:20], "little")
        elif len(decrypted) >= 24:
            real = 24 + ((len(decrypted) - 24) // 16) * 16
        else:
            real = len(decrypted)

        return decrypted[:real]

    async def _recv_abridged(self) -> Optional[bytes]:
        length = await self._recv_tls(1)
        if length is None:
            return None

        length = aes.ctr256_decrypt(length, *self.decrypt)

        if length == b"\x7f":
            length = await self._recv_tls(3)
            if length is None:
                return None
            length = aes.ctr256_decrypt(length, *self.decrypt)

        packet_length = int.from_bytes(length, "little") * 4
        data = await self._recv_tls(packet_length)
        if data is None:
            return None

        return await self.loop.run_in_executor(
            self.crypto_executor,
            aes.ctr256_decrypt,
            data,
            *self.decrypt,
        )


# Subclasses for each packet codec

class TCPMTProxyAbridged(TCPMTProxy):
    packet_codec = AbridgedPacketCodec


class TCPMTProxyIntermediate(TCPMTProxy):
    packet_codec = IntermediatePacketCodec


class TCPMTProxyRandomizedIntermediate(TCPMTProxy):
    packet_codec = RandomizedIntermediatePacketCodec