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
from typing import Optional, Type

from pyrogram import utils

from .proxy import Proxy
from .transport import TCP, TCPAbridged

log = logging.getLogger(__name__)

# tdesktop's protocolDcId (session_private.cpp:254-265): the media cluster
# is the negated dc id, test-mode servers get a further +10000 shift. Only
# the WEB proxy scheme embeds this (TCP._connect_via_web_proxy's nonce);
# other transports address the DC by IP and never see it.
_TEST_MODE_DC_ID_SHIFT = 10000


def _protocol_dc_id(dc_id: int, test_mode: bool, media: bool) -> int:
    value = dc_id + (_TEST_MODE_DC_ID_SHIFT if test_mode else 0)
    return -value if media else value


class Connection:
    MAX_CONNECTION_ATTEMPTS = 3

    def __init__(
        self,
        dc_id: int,
        server_address: str,
        port: int,
        test_mode: bool,
        # Already normalized by pyrogram.connection.proxy.normalize_proxy at
        # the Client boundary - never a raw dict or string here.
        proxy: Optional[Proxy] = None,
        media: bool = False,
        protocol_factory: Type[TCP] = TCPAbridged,
        crypto_executor_workers: int = 1,
        loop: Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        self.dc_id = dc_id
        self.server_address = server_address
        self.port = port
        self.test_mode = test_mode
        self.ipv6 = ":" in server_address
        self.proxy = proxy
        self.media = media
        self.protocol_factory = protocol_factory
        self.crypto_executor_workers = crypto_executor_workers

        self.protocol: Optional[TCP] = None
        self._protocol_dc_id = _protocol_dc_id(dc_id, test_mode, media)

        if isinstance(loop, asyncio.AbstractEventLoop):
            self.loop = loop
        else:
            self.loop = utils.get_event_loop()

    async def connect(self) -> None:
        for i in range(Connection.MAX_CONNECTION_ATTEMPTS):
            self.protocol = self.protocol_factory(
                ipv6=self.ipv6,
                proxy=self.proxy,
                crypto_executor_workers=self.crypto_executor_workers,
                loop=self.loop,
                dc_id=self._protocol_dc_id,
            )

            try:
                log.info("Connecting...")
                await self.protocol.connect((self.server_address, self.port))
            except OSError as e:
                log.warning("Unable to connect due to network issues: %s", e)
                await self.protocol.close()
                await asyncio.sleep(1)
            else:
                log.info("Connected! %s DC%s%s - IPv%s",
                         "Test" if self.test_mode else "Production",
                         self.dc_id,
                         " (media)" if self.media else "",
                         "6" if self.ipv6 else "4")
                break
        else:
            log.warning("Connection failed! Trying again...")
            raise ConnectionError

    async def close(self) -> None:
        await self.protocol.close()
        log.info("Disconnected")

    async def send(self, data: bytes) -> None:
        await self.protocol.send(data)

    async def recv(self) -> Optional[bytes]:
        return await self.protocol.recv()
