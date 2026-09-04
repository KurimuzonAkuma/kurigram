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

from typing import Optional

import pyrogram
from pyrogram import raw
from pyrogram import types
from pyrogram import utils


class EditInlineReplyMarkup:
    async def edit_inline_reply_markup(
        self: "pyrogram.Client",
        inline_message_id: str,
        reply_markup: Optional["types.InlineKeyboardMarkup"] = None
    ) -> bool:
        """Edit only the reply markup of inline messages sent via the bot (for inline bots).

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            inline_message_id (``str``):
                Identifier of the inline message.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

                # Bots only
                await app.edit_inline_reply_markup(
                    inline_message_id,
                    InlineKeyboardMarkup([[
                        InlineKeyboardButton("New button", callback_data="new_data")]]))
        """

        unpacked = utils.unpack_inline_message_id(inline_message_id)

        # Attempt direct chat message edit first when peer and id are available in inline_message_id.
        # This preserves custom emoji icons on buttons, which Telegram's EditInlineBotMessage server actively strips.
        if isinstance(unpacked, raw.types.InputBotInlineMessageID64):
            chat_id = utils.get_channel_id(abs(unpacked.owner_id)) if unpacked.owner_id < 0 else unpacked.owner_id
            msg_id = unpacked.id
            try:
                res = await self.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=msg_id,
                    reply_markup=reply_markup,
                )
                if res:
                    return True
            except Exception:
                pass

        dc_id = unpacked.dc_id

        session = await self.get_session(dc_id, is_media=True)

        return await session.invoke(
            raw.functions.messages.EditInlineBotMessage(
                id=unpacked,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
            ),
            sleep_threshold=self.sleep_threshold
        )
