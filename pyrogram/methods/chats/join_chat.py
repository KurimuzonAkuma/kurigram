#  Kurigram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2023-present Kurigram <https://github.com/KurimuzonAkuma/kurigram>
#
#  This file is part of Kurigram.
#
#  Kurigram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Kurigram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Kurigram.  If not, see <http://www.gnu.org/licenses/>.

from typing import Optional, Union

import pyrogram
from pyrogram import raw
from pyrogram import types


class JoinChat:
    async def join_chat(
        self: "pyrogram.Client",
        chat_id: Union[int, str]
    ) -> Optional["types.Chat"]:
        """Join a group chat or channel.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier for the target chat in form of a *t.me/joinchat/* link, a username of the target
                channel/supergroup (in the format @username) or a chat id of a linked chat (channel or supergroup).

        Returns:
            :obj:`~pyrogram.types.Chat` | ``None``: On success, a chat object is returned.
            ``None`` is returned when the server responds with :obj:`~pyrogram.raw.types.ChatInviteJoinResultOk`.

        Raises:
            ValueError: In case the chat invite link points to a chat you are already in.

        Example:
            .. code-block:: python

                # Join chat via invite link
                await app.join_chat("https://t.me/+AbCdEf0123456789")

                # Join chat via username
                await app.join_chat("pyrogram")

                # Join a linked chat
                await app.join_chat(app.get_chat("pyrogram").linked_chat.id)
        """
        match = self.INVITE_LINK_RE.match(str(chat_id))

        if match:
            chat = await self.invoke(
                raw.functions.messages.ImportChatInvite(
                    hash=match.group(1)
                )
            )

            if isinstance(chat, raw.types.ChatInviteJoinResultOk):
                return None

            if isinstance(chat.chats[0], raw.types.Chat):
                return types.Chat._parse_chat_chat(self, chat.chats[0])
            elif isinstance(chat.chats[0], raw.types.Channel):
                return types.Chat._parse_channel_chat(self, chat.chats[0])
        else:
            chat = await self.invoke(
                raw.functions.channels.JoinChannel(
                    channel=await self.resolve_peer(chat_id)
                )
            )

            if isinstance(chat, raw.types.ChatInviteJoinResultOk):
                return None

            return types.Chat._parse_channel_chat(self, chat.chats[0])
