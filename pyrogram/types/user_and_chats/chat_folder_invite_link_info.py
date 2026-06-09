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

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object


class ChatFolderInviteLinkInfo(Object):
    """Contains information about an invite link to a chat folder.

    Parameters:
        chat_folder_info (:obj:`~pyrogram.types.ChatFolderInfo`):
            Basic information about the chat folder.
            Chat folder identifier will be None if the user didn't have the chat folder yet.

        missing_chats (List of :obj:`~pyrogram.types.Chat`):
            Chats from the link, which aren't added to the folder yet.

        added_chats (List of :obj:`~pyrogram.types.Chat`):
            Chats from the link, which are added to the folder already.
    """

    def __init__(
        self,
        *,
        chat_folder_info: "types.ChatFolderInfo",
        missing_chats: Optional[List["types.Chat"]] = None,
        added_chats: Optional[List["types.Chat"]] = None,
    ):
        self.chat_folder_info = chat_folder_info
        self.missing_chats = missing_chats
        self.added_chats = added_chats

    @staticmethod
    async def _parse(
        client: "pyrogram.Client", invite: "raw.base.chatlists.ChatlistInvite"
    ) -> "ChatFolderInviteLinkInfo":
        if isinstance(invite, raw.types.chatlists.ChatlistInvite):
            title = types.FormattedText._parse(client, invite.title)

            return ChatFolderInviteLinkInfo(
                chat_folder_info=types.Folder(
                    name=title.text,
                    entities=title.entities,
                    icon=invite.emoticon,
                    animate_custom_emoji=not invite.title_noanimate,
                    client=client,
                ),
                missing_chats=types.List(
                    [types.Chat._parse_chat(client, chat) for chat in invite.chats]
                )
                or None,
            )

        if isinstance(invite, raw.types.chatlists.ChatlistInviteAlready):
            chats = {i.id: i for i in invite.chats}

            return ChatFolderInviteLinkInfo(
                chat_folder_info=types.Folder(
                    id=invite.filter_id,
                    client=client,
                ),
                missing_chats=types.List(
                    [
                        types.Chat._parse_chat(client, chats.get(utils.get_raw_peer_id(i)))
                        for i in invite.missing_peers
                    ]
                )
                or None,
                added_chats=types.List(
                    [
                        types.Chat._parse_chat(client, chats.get(utils.get_raw_peer_id(i)))
                        for i in invite.already_peers
                    ]
                )
                or None,
            )
