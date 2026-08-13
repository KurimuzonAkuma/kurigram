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

from typing import Union, AsyncIterator

import pyrogram
from pyrogram import types, raw


class GetCallMembers:
    async def get_call_members(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        limit: int = 0
    ) -> AsyncIterator["types.GroupCallMember"]:
        """Get the members list of a chat call.

        A chat can be either a basic group or a supergroup.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            limit (``int``, *optional*):
                Limits the number of members to be retrieved.

        Returns:
            ``Generator``: On success, a generator yielding :obj:`~pyrogram.types.GroupCallMember` objects is returned.

        Example:
            .. code-block:: python

                # Get members
                async for member in app.get_call_members(chat_id):
                    print(member)
        """
        peer = await self.resolve_peer(chat_id)

        if isinstance(peer, raw.types.InputPeerChannel):
            r = await self.invoke(raw.functions.channels.GetFullChannel(channel=peer))
        elif isinstance(peer, raw.types.InputPeerChat):
            r = await self.invoke(raw.functions.messages.GetFullChat(chat_id=peer.chat_id))
        else:
            raise ValueError("Target chat should be group, supergroup or channel.")

        full_chat = r.full_chat

        if not getattr(full_chat, "call", None):
            raise ValueError("There is no active call in this chat.")

        current = 0
        offset = ""
        total = abs(limit) or (1 << 31) - 1
        limit = min(20, total)

        while True:
            r = await self.invoke(
                raw.functions.phone.GetGroupParticipants(
                    call=full_chat.call,
                    ids=[],
                    sources=[],
                    offset=offset,
                    limit=limit
                ),
                sleep_threshold=60
            )

            users = {u.id: u for u in r.users}
            chats = {c.id: c for c in r.chats}
            members = [
                types.GroupCallMember._parse(self, member, users, chats)
                for member in r.participants
            ]

            if not members:
                return

            offset = r.next_offset

            for member in members:
                yield member

                current += 1

                if current >= total:
                    return
