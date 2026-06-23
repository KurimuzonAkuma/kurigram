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
from pyrogram import raw, types, errors


class JoinChat:
    async def join_chat(
        self: "pyrogram.Client", chat_id: Union[int, str]
    ) -> "types.ChatJoinResult":
        """Adds the current user as a new member to a chat. Private and secret chats can't be joined using this method.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier for the target chat in form of a *t.me/joinchat/* link, a username of the target
                channel/supergroup (in the format @username) or a chat id of a linked chat (channel or supergroup).

        Returns:
            :obj:`~pyrogram.types.ChatJoinResult`: On success, a chat join result object is returned.

        Example:
            .. code-block:: python

                # Join chat via invite link
                await app.join_chat("https://t.me/+AbCdEf0123456789")

                # Join chat via username
                await app.join_chat("pyrogram")

                # Join a linked chat
                await app.join_chat((await app.get_chat("pyrogram")).linked_chat.id)
        """
        match = self.INVITE_LINK_RE.match(str(chat_id))

        if match:
            rpc = raw.functions.messages.ImportChatInvite(hash=match.group(1))
        else:
            rpc = raw.functions.channels.JoinChannel(channel=await self.resolve_peer(chat_id))

        try:
            r = await self.invoke(rpc)
        except errors.InviteRequestSent:
            return types.ChatJoinResultRequestSent()

        return await types.ChatJoinResult._parse(self, r)
