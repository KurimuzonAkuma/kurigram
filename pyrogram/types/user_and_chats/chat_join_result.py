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

from ..object import Object


class ChatJoinResult(Object):
    """Describes result of join of a chat by the current user.

    It can be one of:

    - :obj:`~pyrogram.types.ChatJoinResultSuccess`
    - :obj:`~pyrogram.types.ChatJoinResultRequestSent`
    - :obj:`~pyrogram.types.ChatJoinResultGuardBotApprovalRequired`
    - :obj:`~pyrogram.types.ChatJoinResultDeclined`
    """

    def __init__(self):
        super().__init__()

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        result: "raw.base.messages.ChatInviteJoinResult"
    ) -> "ChatJoinResult":
        if isinstance(result, raw.types.messages.ChatInviteJoinResultOk):
            return ChatJoinResultSuccess(
                chat=types.Chat._parse_chat(client, result.updates.chats[0])
            )
        if isinstance(result, raw.types.messages.ChatInviteJoinResultWebView):
            users = {i.id: i for i in result.users}

            return ChatJoinResultGuardBotApprovalRequired(
                bot=types.User._parse(client, users[result.bot_id]),
                url=result.webview.url,
                query_id=str(result.webview.query_id) if result.webview.query_id else None
            )


class ChatJoinResultSuccess(ChatJoinResult):
    """Contains information about a joiner member of a chat.

    Parameters:
        chat (:obj:`~pyrogram.types.Chat`):
            Information about the joined chat.
    """

    def __init__(
        self,
        *,
        chat: "types.Chat",
    ):
        super().__init__()

        self.chat = chat

class ChatJoinResultRequestSent(ChatJoinResult):
    """The join request was sent and have to be approved by administrators of the chat."""

    def __init__(
        self,
    ):
        super().__init__()


class ChatJoinResultGuardBotApprovalRequired(ChatJoinResult):
    """An approval from a guard bot through a Web App is required to join the chat.

    Parameters:
        bot (:obj:`~pyrogram.types.User`):
            Information about the joined chat.

        url (``str``):
            The URL of the Web App to open.

        query_id (``str``):
            Unique identifier of the join request.
    """

    def __init__(
        self,
        *,
        bot: "types.User",
        url: str,
        query_id: str
    ):
        super().__init__()

        self.bot = bot
        self.url = url
        self.query_id = query_id

class ChatJoinResultDeclined(Object):
    """The join was declined by the guard bot."""

    def __init__(
        self,
    ):
        super().__init__()
