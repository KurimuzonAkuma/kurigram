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

from typing import List, Optional, Union
import pyrogram
from pyrogram import raw, types


class CreateFolderInviteLink:
    async def create_folder_invite_link(
        self: "pyrogram.Client",
        chat_folder_id: int,
        chat_ids: List[Union[int, str]],
        name: Optional[str] = None,
    ) -> "types.FolderInviteLink":
        """Create a new invite link for a chat folder.

        .. note::

            A link can be created for a chat folder if it has only pinned and included chats.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_folder_id (``int``):
                Unique identifier (int) of the target folder.

            chat_ids (List of ``int`` | ``str``):
                Identifiers of chats to be accessible by the invite link.
                Use :meth:`~pyrogram.Client.get_chats_for_folder_invite_link` to get suitable chats.

            name (``str``, *optional*):
                Name of the link, 0-32 characters.

        Returns:
            :obj:`~pyrogram.types.FolderInviteLink`: On success, information about the invite link is returned.

        Example:
            .. code-block:: python

                # Create new folder link
                await app.create_folder_invite_link(folder_id, [123456789, 987654321])
        """
        r = await self.invoke(
            raw.functions.chatlists.ExportChatlistInvite(
                chatlist=raw.types.InputChatlistDialogFilter(filter_id=chat_folder_id),
                title=name or "",
                peers=[await self.resolve_peer(i) for i in chat_ids],
            )
        )

        return types.FolderInviteLink._parse(r.invite)
