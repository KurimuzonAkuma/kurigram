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
from pyrogram import errors, raw


class SetChatDirectMessagesGroup:
    async def set_chat_direct_messages_group(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        paid_message_star_count: int = 0,
        is_enabled: Optional[bool] = None,
    ) -> bool:
        """Change direct messages group settings for a channel chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            paid_message_star_count (``bool``):
                The new number of Telegram Stars that must be paid for each message that is sent to the direct messages chat unless the sender is an administrator of the channel chat, 0-10000.

            is_enabled (``bool``, *optional*):
                Pass True if the direct messages group is enabled for the channel chat.
                Pass False otherwise

        Returns:
            ``bool``: True on success. False otherwise.

        Example:
            .. code-block:: python

                # Enable direct messages
                await app.set_chat_direct_messages_group(chat_id, is_enabled=True)
        """
        try:
            r = await self.invoke(
                raw.functions.channels.UpdatePaidMessagesPrice(
                    channel=await self.resolve_peer(chat_id),
                    send_paid_messages_stars=paid_message_star_count,
                    broadcast_messages_allowed=is_enabled
                )
            )

            return bool(r)
        except errors.RPCError:
            return False
