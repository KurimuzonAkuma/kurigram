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
from typing import Optional, Tuple

from pyrogram.connection.proxy import Proxy
from pyrogram.connection.transport.tcp.tcp import INTERMEDIATE_PADDED_OBFUSCATE_TAG, TCP

log = logging.getLogger(__name__)


class TCPIntermediatePadded(TCP):
    # Lets TCP._connect_via_web_proxy use this class over a WEB proxy
    #  (proxy={"scheme": "web", ...}) unmodified - Telegram's protocol requires
    #  this exact tag/framing for dd-prefixed (random-padding) secrets
    #  specifically, which TCP._connect_via_web_proxy checks.
    OBFUSCATE_TAG = INTERMEDIATE_PADDED_OBFUSCATE_TAG

    def __init__(
        self,
        ipv6: bool = False,
        proxy: Optional[Proxy] = None,
        crypto_executor_workers: int = 1,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        dc_id: Optional[int] = None,
    ) -> None:
        super().__init__(ipv6, proxy, crypto_executor_workers, loop, dc_id=dc_id)

    async def connect(self, address: Tuple[str, int]) -> None:
        self.marker_event.clear()
        await super().connect(address)
        if not self.is_web_proxy:
            # Over a WEB proxy the obfuscated2 header TCP._connect_via_web_proxy
            #  already sent embeds this same tag - sending it again here would
            #  corrupt the stream with extra, unobfuscated bytes.
            await super().send(INTERMEDIATE_PADDED_OBFUSCATE_TAG, wait_for_marker=False)
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
