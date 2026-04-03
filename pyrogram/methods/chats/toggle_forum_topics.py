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

from typing import Union

import pyrogram
from pyrogram import errors, raw


class ToggleForumTopics:
    async def toggle_forum_topics(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        is_forum: bool = False,
        has_forum_tabs: bool = False
    ) -> bool:
        """Enable or disable forum functionality in a supergroup.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            is_forum (``bool``):
                The new status.
                Pass True to enable forum topics.
                Defaults to False.

            has_forum_tabs (``bool``):
                Whether to enable or disable tabs in the forum.
                Defaults to False.

        Returns:
            ``bool``: True on success. False otherwise.

        Example:
            .. code-block:: python

                # Change status of topics to disabled
                await app.toggle_forum_topics(is_forum=False)

                # Change status of topics to enabled
                await app.toggle_forum_topics(is_forum=True)
        """
        try:
            r = await self.invoke(
                raw.functions.channels.ToggleForum(
                    channel=await self.resolve_peer(chat_id),
                    enabled=is_forum,
                    tabs=has_forum_tabs
                )
            )

            return bool(r)
        except errors.RPCError:
            return False
