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


class GetTopChats:
    async def get_top_chats(
        self: "pyrogram.Client",
        category: "enums.TopChatCategory",
        limit: int = 0,
    ) -> AsyncGenerator["types.Chat", None]:
        """Returns a list of frequently used chats.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            category (:obj:`~pyrogram.enums.TopChatCategory`):
                Category of chats to be returned.

            limit (``int``, *optional*):
                The maximum number of chats to be returned.
                By default, no limit is applied and all chats are returned.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Chat` objects.

        Example:
            .. code-block:: python

                # Iterate through all top chats in the "users" category
                async for chat in app.get_top_chats(enums.TopChatCategory.USERS):
                    print(chat.full_name)
        """
        current = 0
        total = limit or (1 << 31) - 1
        limit = min(30, total)

        offset = 0

        while True:
            r = await self.invoke(
                raw.functions.contacts.GetTopPeers(
                    offset=offset,
                    limit=limit,
                    hash=0,
                    correspondents=category == enums.TopChatCategory.USERS,
                    bots_pm=category == enums.TopChatCategory.BOTS,
                    bots_inline=category == enums.TopChatCategory.INLINE_BOTS,
                    phone_calls=category == enums.TopChatCategory.CALLS,
                    forward_users=category == enums.TopChatCategory.FORWARD_CHATS,
                    forward_chats=category == enums.TopChatCategory.FORWARD_CHATS,
                    groups=category == enums.TopChatCategory.GROUPS,
                    channels=category == enums.TopChatCategory.CHANNELS,
                    bots_app=category == enums.TopChatCategory.WEB_APP_BOTS,
                    bots_guestchat=category == enums.TopChatCategory.GUEST_BOTS,
                ),
                sleep_threshold=60
            )

            if not isinstance(r, raw.types.contacts.TopPeers):
                return

            users = {i.id: i for i in r.users}
            chats = {i.id: i for i in r.chats}

            chats = []

            for cat in r.categories:
                for top_peer in cat.peers:
                    peer_id = utils.get_raw_peer_id(top_peer.peer)

                    chats.append(types.Chat._parse_chat(self, users.get(peer_id) or chats.get(peer_id)))

            if not chats:
                return

            offset += len(chats)

            for chat in chats:
                yield chat

                current += 1

                if current >= total:
                    return
