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
import pyrogram
from pyrogram import raw, types


class CheckChatFolderInviteLink:
    async def check_chat_folder_invite_link(
        self: "pyrogram.Client",
        invite_link: str,
    ) -> "types.ChatFolderInviteLinkInfo":
        """Checks the validity of an invite link for a chat folder and returns information about the corresponding chat folder.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            invite_link (``str``):
                Invite link to be checked.

        Returns:
            :obj:`~pyrogram.types.ChatFolderInviteLinkInfo`: Information about the chat folder corresponding to the invite link.

        Raises:
            BadRequest: In case the folder invite link not exists.
            ValueError: In case the folder invite link is invalid.
        """
        match = self.CHATLIST_INVITE_RE.match(invite_link)

        if match:
            slug = match.group(1)
        else:
            raise ValueError("Invalid folder invite link")

        r = await self.invoke(
            raw.functions.chatlists.CheckChatlistInvite(
                slug=slug
            )
        )

        return await types.ChatFolderInviteLinkInfo._parse(self, r)
