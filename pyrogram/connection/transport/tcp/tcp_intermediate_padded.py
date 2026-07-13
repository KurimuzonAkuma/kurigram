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
import os
from struct import pack, unpack
from typing import Optional, Tuple, Union

from .tcp import TCP, ProxyDict

log = logging.getLogger(__name__)


class TCPIntermediatePadded(TCP):
    def __init__(
        self,
        ipv6: bool = False,
        proxy: Optional[Union[str, ProxyDict]] = None,
        crypto_executor_workers: int = 1,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> None:
        super().__init__(ipv6, proxy, crypto_executor_workers, loop)

    async def connect(self, address: Tuple[str, int]) -> None:
        self.marker_event.clear()
        await super().connect(address)
        await super().send(b"\xdd" * 4, wait_for_marker=False)
        self.marker_event.set()

    async def send(self, data: bytes, *args) -> None:
        padding = os.urandom(os.urandom(1)[0] & 0x0F)
        await super().send(pack("<i", len(data) + len(padding)) + data + padding)

    async def recv(self, length: int = 0) -> Optional[bytes]:
        length = await super().recv(4)

        if length is None:
            return None

        length = unpack("<i", length)[0]
        data = await super().recv(length)

        if data is None:
            return None

        if length < 24:
            if length >= 8 and data[:4] == b"\xff\xff\xff\xff":
                return data[:8]
            return data[:4]

        if data[:8] != b"\x00" * 8:
            strip = (length - 24) % 16

            if strip:
                data = data[:-strip]

        return data
