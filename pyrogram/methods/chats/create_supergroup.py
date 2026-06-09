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

from typing import Optional

import pyrogram
from pyrogram import raw, types


class CreateSupergroup:
    async def create_supergroup(
        self: "pyrogram.Client",
        title: str,
        description: str = "",
        is_forum: Optional[bool] = None,
        message_auto_delete_time: Optional[int] = None,
        for_import: Optional[bool] = None
    ) -> "types.Chat":
        """Create a new supergroup.

        .. note::

            If you want to create a new basic group, use :meth:`~pyrogram.Client.create_group` instead.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            title (``str``):
                The supergroup title.

            description (``str``, *optional*):
                The supergroup description.

            is_forum (``bool``, *optional*):
                Pass True to create a forum supergroup chat.

            message_auto_delete_time (``int``, *optional*):
                Message auto-delete time value, in seconds, must be from 0 up to 365 * 86400 and be divisible by 86400.
                If None, then messages aren't deleted automatically.

            for_import (``bool``, *optional*):
                Pass True to create a supergroup for importing messages.

        Returns:
            :obj:`~pyrogram.types.Chat`: On success, a chat object is returned.

        Example:
            .. code-block:: python

                await app.create_supergroup("Supergroup Title", "Supergroup Description")
        """
        r = await self.invoke(
            raw.functions.channels.CreateChannel(
                title=title,
                about=description,
                megagroup=True,
                for_import=for_import,
                forum=is_forum,
                ttl_period=message_auto_delete_time,
            )
        )

        return types.Chat._parse_chat(self, r.chats[0])
