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
from pyrogram import raw


class GetChatMusicCount:
    async def get_chat_music_count(
        self: "pyrogram.Client", chat_id: Union[int, str]
    ) -> int:
        """Get the total count of saved music entries for a chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

        Returns:
            ``int``: On success, the total count is returned.

        Example:
            .. code-block:: python

                count = await app.get_chat_music_count("me")
                print(count)
        """
        peer_id = await self.resolve_peer(chat_id)

        r = await self.invoke(
            raw.functions.users.GetSavedMusic(
                id=peer_id,
                offset=0,
                limit=1,
                hash=0,
            )
        )

        return r.count
