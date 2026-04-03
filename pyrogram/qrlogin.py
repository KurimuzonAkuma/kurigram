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
import base64
import datetime
import logging
from typing import List, Optional

import pyrogram
from pyrogram import filters, handlers, raw, types

log = logging.getLogger(__name__)


class QRLogin:
    def __init__(self, client, except_ids: List[int] = []):
        self.client: "pyrogram.Client" = client
        self.except_ids: List[int] = except_ids
        self.r: "raw.base.auth.LoginToken" = None

    async def recreate(self):
        self.r = await self.client.invoke(
            raw.functions.auth.ExportLoginToken(
                api_id=self.client.api_id,
                api_hash=self.client.api_hash,
                except_ids=self.except_ids,
            )
        )

    async def wait(self, timeout: float = None) -> Optional["types.User"]:
        if timeout is None:
            timeout = self.r.expires - int(datetime.datetime.now().timestamp())

        event = asyncio.Event()

        async def raw_handler(client, update, users, chats):
            event.set()

        handler = self.client.add_handler(
            handlers.RawUpdateHandler(
                raw_handler,
                filters=filters.create(lambda _, __, u: isinstance(u, raw.types.UpdateLoginToken)),
            )
        )

        await self.client.dispatcher.start()

        try:
            await asyncio.wait_for(event.wait(), timeout=timeout)
        finally:
            self.client.remove_handler(*handler)
            await self.client.dispatcher.stop(clear_handlers=False)

        r = await self.client.invoke(
            raw.functions.auth.ExportLoginToken(
                api_id=self.client.api_id,
                api_hash=self.client.api_hash,
                except_ids=self.except_ids,
            )
        )

        if isinstance(r, raw.types.auth.LoginTokenMigrateTo):
            dc_option = await self.client.get_dc_option(r.dc_id, ipv6=self.client.ipv6)
            await self.client.session.stop()

            self.client.session = await self.client.get_session(
                dc_id=r.dc_id,
                server_address=dc_option.ip_address,
                port=dc_option.port,
                export_authorization=False,
                temporary=True
            )

            await self.client.storage.dc_id(r.dc_id)
            await self.client.storage.server_address(dc_option.ip_address)
            await self.client.storage.port(dc_option.port)
            await self.client.storage.auth_key(self.client.session.auth_key)       

            r = await self.client.invoke(
                raw.functions.auth.ImportLoginToken(token=r.token)
            )

        if isinstance(r, raw.types.auth.LoginTokenSuccess):
            user = types.User._parse(self.client, r.authorization.user)

            await self.client.storage.user_id(user.id)
            await self.client.storage.is_bot(False)

            return user

        raise TypeError("Unexpected login token response: {}".format(r))

    @property
    def url(self) -> str:
        return f"tg://login?token={base64.urlsafe_b64encode(self.r.token).decode('utf-8')}"
