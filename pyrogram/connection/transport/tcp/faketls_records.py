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

"""The TLS record layer an ee-prefixed MTProxy speaks once its greeting is answered.

Nothing here is encrypted: the payload is the same obfuscated2 stream a plain
MTProxy reads, cut into records that look like TLS application data from the
outside. Ported from TDLib's `ObfuscatedTransport`, whose reader rejects any
record that is not application data.
https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/TcpTransport.cpp#L173-L214
https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/TlsReaderByteFlow.cpp#L15-L36
"""

from typing import Final, Optional, Protocol, Tuple

# The five bytes every record opens with: content type 0x17 for application data
#  and the legacy version 0x0303, then a 2-byte big-endian length. TDLib writes
#  them from a literal and reads them back the same way.
#  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/TcpTransport.cpp#L201-L204
#  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/TlsReaderByteFlow.cpp#L16-L28
APPLICATION_DATA_PREFIX: Final[bytes] = b"\x17\x03\x03"
RECORD_LENGTH_SIZE: Final[int] = 2
RECORD_HEADER_SIZE: Final[int] = len(APPLICATION_DATA_PREFIX) + RECORD_LENGTH_SIZE

# A real client sends one of these between its handshake and its first
#  application record, so the emulation sends one too - once, and never again.
#  TDLib prepends the same six bytes behind an `is_first_tls_packet_` flag.
#  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/TcpTransport.cpp#L206-L210
CHANGE_CIPHER_SPEC: Final[bytes] = b"\x14\x03\x03\x00\x01\x01"

# TDLib's `MAX_TLS_PACKET_LENGTH`, counting whatever is prepended to the payload.
#  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/TcpTransport.h#L162
_MAX_RECORD_PAYLOAD: Final[int] = 2878

# The two segments a proxy answers the greeting with, each followed by its own
#  2-byte length: the ServerHello, then a change-cipher-spec glued to the first
#  application record. Both are hashed, so they are read rather than skipped.
#  https://github.com/tdlib/td/blob/d1085f9cebc5a62379991ae1652673954f229c1f/td/mtproto/TlsInit.cpp#L616-L641
GREETING_RESPONSE_PREFIXES: Final[Tuple[bytes, ...]] = (
    b"\x16\x03\x03",
    CHANGE_CIPHER_SPEC + APPLICATION_DATA_PREFIX,
)


class ReadExactly(Protocol):
    async def __call__(self, length: int) -> Optional[bytes]: ...


class FakeTlsRecords:
    def __init__(self, read_exactly: ReadExactly, *, prologue: bytes) -> None:
        self._read_exactly = read_exactly

        # The obfuscated2 header, which rides inside the first record rather than
        #  in one of its own: TDLib prepends it the same way, and a lone 64-byte
        #  record right after the greeting is a shape nothing else produces.
        self._prologue = prologue

        self._buffer = bytearray()
        self._sent_change_cipher_spec = False

    def wrap(self, data: bytes) -> bytes:
        payload = self._prologue + data
        self._prologue = b""

        wire = bytearray()

        if not self._sent_change_cipher_spec:
            self._sent_change_cipher_spec = True
            wire += CHANGE_CIPHER_SPEC

        for start in range(0, len(payload), _MAX_RECORD_PAYLOAD):
            chunk = payload[start : start + _MAX_RECORD_PAYLOAD]
            wire += APPLICATION_DATA_PREFIX + len(chunk).to_bytes(RECORD_LENGTH_SIZE, "big") + chunk

        return bytes(wire)

    async def recv(self, length: int) -> Optional[bytes]:
        # A record boundary has nothing to do with a packet boundary, so reads are
        #  served out of a buffer and a record is pulled in only when it runs dry.
        while len(self._buffer) < length:
            record = await self._read_record()

            if record is None:
                return None

            self._buffer += record

        data = bytes(self._buffer[:length])
        del self._buffer[:length]

        return data

    async def _read_record(self) -> Optional[bytes]:
        header = await self._read_exactly(RECORD_HEADER_SIZE)

        if header is None:
            return None

        if header[: len(APPLICATION_DATA_PREFIX)] != APPLICATION_DATA_PREFIX:
            msg = f"fake-TLS: expected an application-data record, got {header.hex()}"
            raise OSError(msg)

        length = int.from_bytes(header[-RECORD_LENGTH_SIZE:], "big")

        return await self._read_exactly(length)
