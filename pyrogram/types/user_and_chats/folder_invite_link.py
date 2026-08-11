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

from typing import List, Optional

from pyrogram import raw, types, utils
from ..object import Object


class FolderInviteLink(Object):
    """Contains a chat folder invite link.

    Parameters:
        invite_link (``str``):
            The chat folder invite link.

        name (``str``, *optional*):
            Name of the link.

        chat_ids (List of ``int``, *optional*):
            Identifiers of chats, included in the link.
    """
    def __init__(
        self,
        *,
        invite_link: str,
        name: Optional[str] = None,
        chat_ids: Optional[List[int]] = None
    ):
        super().__init__()

        self.invite_link = invite_link
        self.name = name
        self.chat_ids = chat_ids

    @staticmethod
    def _parse(invite: "raw.base.ExportedChatlistInvite") -> "FolderInviteLink":
        return FolderInviteLink(
            invite_link=invite.url,
            name=invite.title,
            chat_ids=types.List([utils.get_peer_id(peer) for peer in invite.peers])
        )
