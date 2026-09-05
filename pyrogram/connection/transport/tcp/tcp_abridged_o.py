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
from typing import Optional, Tuple

import pyrogram
from pyrogram.connection.proxy import Proxy
from pyrogram.connection.transport.tcp.tcp import (
    ABRIDGED_OBFUSCATE_TAG,
    TCP,
    finalize_obfuscated2_tag,
    generate_obfuscated2_nonce,
)
from pyrogram.crypto import aes

log = logging.getLogger(__name__)


class TCPAbridgedO(TCP):
    def __init__(
        self,
        ipv6: bool,
        proxy: Optional[Proxy] = None,
        crypto_executor_workers: int = 1,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        dc_id: Optional[int] = None,
    ) -> None:
        super().__init__(ipv6, proxy, crypto_executor_workers, loop, dc_id=dc_id)

        self.encrypt = None
        self.decrypt = None

    async def connect(self, address: Tuple[str, int]) -> None:
        self.marker_event.clear()
        await super().connect(address)

        nonce = generate_obfuscated2_nonce()
        nonce[56:60] = ABRIDGED_OBFUSCATE_TAG

        temp = bytearray(nonce[55:7:-1])

        self.encrypt = (nonce[8:40], nonce[40:56], bytearray(1))
        self.decrypt = (temp[0:32], temp[32:48], bytearray(1))

        nonce[56:64] = finalize_obfuscated2_tag(nonce, encrypt=self.encrypt)

        await super().send(nonce, wait_for_marker=False)
        self.marker_event.set()

    async def send(self, data: bytes, *args) -> None:
        encrypt = self.encrypt

        if encrypt is None:
            msg = "`send()` requires `connect()` to have run first"
            raise RuntimeError(msg)

        length = len(data) // 4
        data = (
            bytes([length]) if length <= 126 else b"\x7f" + length.to_bytes(3, "little")
        ) + data
        payload = await self.loop.run_in_executor(
            self.crypto_executor, aes.ctr256_encrypt, data, *encrypt
        )

        await super().send(payload)

    async def recv(self, length: int = 0) -> Optional[bytes]:
        decrypt = self.decrypt

        if decrypt is None:
            msg = "`recv()` requires `connect()` to have run first"
            raise RuntimeError(msg)

        length = await super().recv(1)

        if length is None:
            return None

        length = aes.ctr256_decrypt(length, *decrypt)

        if length == b"\x7f":
            length = await super().recv(3)

            if length is None:
                return None

            length = aes.ctr256_decrypt(length, *decrypt)

        data = await super().recv(int.from_bytes(length, "little") * 4)

        if data is None:
            return None

        return await self.loop.run_in_executor(
            self.crypto_executor, aes.ctr256_decrypt, data, *decrypt
        )
