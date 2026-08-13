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

from typing import AsyncIterator, Optional, Union

import pyrogram
from pyrogram import raw, types, utils


class GetDirectMessagesTopics:
    async def get_direct_messages_topics(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        limit: int = 0,
        exclude_pinned: Optional[bool] = None
    ) -> AsyncIterator["types.DirectMessagesTopic"]:
        """Get one or more topic from a direct messages channel chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            limit (``int``, *optional*):
                Limits the number of topics to be retrieved.
                By default, no limit is applied and all topics are returned.

            exclude_pinned (``bool``, *optional*):
                Exclude pinned topics.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.DirectMessagesTopic` objects.

        Example:
            .. code-block:: python

                # Iterate through all topics
                async for topic in app.get_direct_messages_topics(chat_id):
                    print(topic)
        """
        current = 0
        total = limit or (1 << 31) - 1
        limit = min(100, total)

        offset_date = 0
        offset_id = 0
        offset_peer = raw.types.InputPeerEmpty()

        while True:
            r = await self.invoke(
                raw.functions.messages.GetSavedDialogs(
                    offset_date=offset_date,
                    offset_id=offset_id,
                    offset_peer=offset_peer,
                    limit=limit,
                    hash=0,
                    exclude_pinned=exclude_pinned,
                    parent_peer=await self.resolve_peer(chat_id)
                )
            )

            users = {i.id: i for i in r.users}
            chats = {i.id: i for i in r.chats}

            messages = {}

            for message in r.messages:
                if isinstance(message, raw.types.MessageEmpty):
                    continue

                messages[message.id] = await types.Message._parse(self, message, users, chats)

            topics = []

            for topic in r.dialogs:
                topics.append(types.DirectMessagesTopic._parse(client=self, topic=topic, messages=messages, users=users, chats=chats))

            if not topics:
                return

            last = topics[-1]

            offset_id = last.last_message.id
            offset_date = utils.datetime_to_timestamp(last.last_message.date)
            offset_peer = await self.resolve_peer(last.id)

            for topic in topics:
                yield topic

                current += 1

                if current >= total:
                    return
