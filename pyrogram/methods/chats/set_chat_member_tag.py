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


class SetChatMemberTag:
    async def set_chat_member_tag(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        user_id: Union[int, str],
        tag: Optional[str] = None,
    ) -> bool:
        """Use this method to set a tag for a regular member in a group or a supergroup.

        .. note::

            The bot must be an administrator in the chat for this to work and must have the ``can_manage_tags`` administrator right.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.
                For a contact that exists in your Telegram address book you can use his phone number (str).

            tag (``str``, *optional*):
                New tag for the member, 0-16 characters, emoji are not allowed.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.set_chat_member_tag(chat_id, user_id, "Cool guy")
        """
        chat_id = await self.resolve_peer(chat_id)
        user_id = await self.resolve_peer(user_id)

        await self.invoke(
            raw.functions.messages.EditChatParticipantRank(
                peer=chat_id, participant=user_id, rank=tag or ""
            )
        )

        return True
