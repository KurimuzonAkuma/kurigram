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

from pyrogram.connection.proxy import Proxy
from pyrogram.connection.transport.tcp.tcp import ABRIDGED_OBFUSCATE_TAG, TCP

log = logging.getLogger(__name__)


class TCPAbridged(TCP):
    # Lets TCP._connect_via_web_proxy use this class over a WEB proxy
    #  (proxy={"scheme": "web", ...}) unmodified.
    OBFUSCATE_TAG = ABRIDGED_OBFUSCATE_TAG

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
            #  corrupt the stream with an extra, unobfuscated byte.
            await super().send(b"\xef", wait_for_marker=False)
        self.marker_event.set()

    async def send(self, data: bytes, *args) -> None:
        length = len(data) // 4

        await super().send(
            (bytes([length])
             if length <= 126
             else b"\x7f" + length.to_bytes(3, "little"))
            + data
        )

    async def recv(self, length: int = 0) -> Optional[bytes]:
        length = await super().recv(1)

        if length is None:
            return None

        if length == b"\x7f":
            length = await super().recv(3)

            if length is None:
                return None

        return await super().recv(int.from_bytes(length, "little") * 4)
