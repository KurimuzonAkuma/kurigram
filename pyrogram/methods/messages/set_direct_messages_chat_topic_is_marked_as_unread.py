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

from datetime import datetime
from typing import Union

import pyrogram
from pyrogram import raw


class SetDirectMessagesChatTopicIsMarkedAsUnread:
    async def set_direct_messages_chat_topic_is_marked_as_unread(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        topic_id: int,
        is_marked_as_unread: bool = True
    ) -> int:
        """Change the marked as unread state of the topic in a channel direct messages chat administered by the current user.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            topic_id (``int``):
                Identifier of the topic which messages will be fetched.

            is_marked_as_unread (``bool``, *optional*):
                Pass True to mark the topic as unread.
                Pass False to mark the topic as read.
                Defaults to True.

        Returns:
            ``bool``: True on success

        Example:
            .. code-block:: python

                # Mark the topic as unread
                await app.set_direct_messages_chat_topic_is_marked_as_unread(chat_id, topic_id)
        """
        r = await self.invoke(
            raw.functions.messages.MarkDialogUnread(
                parent_peer=await self.resolve_peer(chat_id),
                peer=await self.resolve_peer(topic_id),
                unread=is_marked_as_unread
            )
        )

        return r
