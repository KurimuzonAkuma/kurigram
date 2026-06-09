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

from typing import AsyncGenerator

import pyrogram
from pyrogram import enums, raw, types, utils


class GetBlockedMessageSenders:
    async def get_blocked_message_senders(
        self: "pyrogram.Client",
        block_list: "enums.BlockList" = enums.BlockList.MAIN,
        offset: int = 0,
        limit: int = 0,
    ) -> AsyncGenerator["types.Chat", None]:
        """Returns users and chats that were blocked by the current user.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            block_list (:obj:`~pyrogram.enums.BlockList`, *optional*):
                The block list from which to return users.

            offset (``int``, *optional*):
                Number of users and chats to skip in the result, must be non-negative.

            limit (``int``, *optional*):
                The maximum number of users and chats to return.

        Returns:
            AsyncGenerator of :obj:`~pyrogram.types.Chat`: An async generator that yields Chat objects.

        Example:
            .. code-block:: python

                async for chat in app.get_blocked_message_senders():
                    print(chat)
        """

        current = 0
        total = abs(limit) or (1 << 31) - 1
        limit = min(100, total)

        while True:
            r = await self.invoke(
                raw.functions.contacts.GetBlocked(
                    offset=offset,
                    limit=limit,
                    my_stories_from=block_list == enums.BlockList.STORIES,
                )
            )

            if not r.blocked:
                return

            users = {i.id: i for i in r.users}
            chats = {i.id: i for i in r.chats}

            offset += len(r.blocked)

            for blocked_user in r.blocked:
                peer_id = utils.get_raw_peer_id(blocked_user.peer_id)

                yield types.Chat._parse_chat(self, users.get(peer_id) or chats.get(peer_id))

                current += 1

                if current >= total:
                    return
