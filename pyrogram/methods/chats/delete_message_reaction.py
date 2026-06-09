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

from typing import Optional, Union

import pyrogram
from pyrogram import raw


class DeleteMessageReaction:
    async def delete_message_reaction(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        *,
        user_id: Optional[Union[int, str]] = None,
        actor_chat_id: Optional[Union[int, str]] = None,
    ) -> bool:
        """Use this method to remove a reaction from a message in a group or a supergroup chat.

        .. note::

            The bot must have the `can_delete_messages` administrator right in the chat.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the target message.

            user_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the user whose reaction will be removed, if the reaction were added by a user.

            actor_chat_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the chat whose reaction will be removed, if the reaction were added by a chat.

        Returns:
            ``bool``: True on success, False otherwise.
        """
        peer = None

        if user_id is not None:
            peer = await self.resolve_peer(user_id)

            if not isinstance(peer, (raw.types.InputPeerUser, raw.types.InputPeerSelf)):
                return False
        elif actor_chat_id is not None:
            peer = await self.resolve_peer(actor_chat_id)

            if not isinstance(peer, raw.types.InputPeerChannel):
                return False
        else:
            raise ValueError("Invalid user_id or actor_chat_id")

        r = await self.invoke(
            raw.functions.messages.DeleteParticipantReaction(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
                participant=peer,
            )
        )

        return bool(r)
