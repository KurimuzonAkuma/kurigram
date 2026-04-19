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
import re
from typing import List

import pyrogram
from pyrogram import raw, types


class GetFolderChannels:
    async def get_folder_channels(
        self: "pyrogram.Client",
        link: str,
    ) -> List["types.Chat"]:
        """Get channels and groups inside a folder invite link.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            link (``str``):
                Invite link of the folder.

        Returns:
            List of :obj:`~pyrogram.types.Chat`: On success, list of chats is returned.

        Raises:
            BadRequest: In case the folder invite link not exists.
            ValueError: In case the folder invite link is invalid.

        Example:
            .. code-block:: python

                # Get all channels in a folder
                chats = await app.get_folder_channels("t.me/addlist/ebXQ0Q0I3RnGQ")

                for chat in chats:
                    print(chat.title)
        """
        match = re.match(r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/(?:addlist/|\+))([\w-]+)$", link)

        if match:
            slug = match.group(1)
        elif isinstance(link, str):
            slug = link
        else:
            raise ValueError("Invalid folder invite link")

        r = await self.invoke(
            raw.functions.chatlists.CheckChatlistInvite(
                slug=slug
            )
        )

        if isinstance(r, raw.types.chatlists.ChatlistInviteAlready):
            raw_chats = r.chats
        else:
            raw_chats = r.chats

        return types.List(
            [
                types.Chat._parse_chat(self, chat)
                for chat in raw_chats
            ]
        )