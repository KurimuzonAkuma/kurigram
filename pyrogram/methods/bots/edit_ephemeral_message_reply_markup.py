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
from pyrogram import raw, types, utils


class EditEphemeralMessageReplyMarkup:
    async def edit_ephemeral_message_reply_markup(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        receiver_user_id: Union[int, str],
        ephemeral_message_id: int,
        reply_markup: Optional["types.InlineKeyboardMarkup"] = None,
    ) -> Optional["types.Message"]:
        """Use this method to edit only the reply markup of an ephemeral message.
        Note that it is not guaranteed that the user will receive the message edit event, especially if they are offline.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            receiver_user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the user who received the message.

            ephemeral_message_id (``int``):
                Identifier of the ephemeral message to edit.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            :obj:`~pyrogram.types.Message` | ``None``: On success, the edited message is returned,
            otherwise, in case the server answered with no message, None is returned.

        Example:
            .. code-block:: python

                from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

                await app.edit_ephemeral_message_reply_markup(
                    chat_id, receiver_user_id, message_id,
                    InlineKeyboardMarkup([[
                        InlineKeyboardButton("New button", callback_data="new_data")]]))
        """
        r = await self.invoke(
            raw.functions.ephemeral.EditMessage(
                peer=await self.resolve_peer(chat_id),
                receiver_id=await self.resolve_peer(receiver_user_id),
                id=ephemeral_message_id,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
            )
        )

        messages = await utils.parse_messages(client=self, messages=r)

        return messages[0] if messages else None
