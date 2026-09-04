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
from pyrogram import raw, types

from ..object import Object


class InlineKeyboardMarkup(Object):
    """An inline keyboard that appears right next to the message it belongs to.

    Parameters:
        inline_keyboard (List of List of :obj:`~pyrogram.types.InlineKeyboardButton`):
            List of button rows, each represented by a List of InlineKeyboardButton objects.

        force_reply (``bool``, *optional*):
            Pass *True* if the reply interface must be shown to the user, as if they had manually selected the bot's message and tapped 'Reply'.
            The value of the field can't be changed when the inline keyboard is edited.
    """

    def __init__(
        self,
        inline_keyboard: List[List["types.InlineKeyboardButton"]],
        force_reply: Optional[bool] = None,
    ):
        super().__init__()

        self.inline_keyboard = inline_keyboard
        self.force_reply = force_reply

    @staticmethod
    def read(reply_markup: "raw.types.ReplyInlineMarkup"):
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton.read(j) for j in i.buttons] for i in reply_markup.rows
            ],
            force_reply=reply_markup.force_reply,
        )

    async def write(self, client: "pyrogram.Client"):
        rows = []

        for r in self.inline_keyboard:
            buttons = []

            for b in r:
                buttons.append(await b.write(client))

            rows.append(raw.types.KeyboardInlineButtonRow(buttons=buttons))

        return raw.types.ReplyInlineMarkup(rows=rows, force_reply=self.force_reply)

        # There seems to be a Python issues with nested async comprehensions.
        # See: https://bugs.python.org/issue33346
        #
        # return raw.types.ReplyInlineMarkup(
        #     rows=[raw.types.KeyboardButtonRow(
        #         buttons=[await j.write(client) for j in i]
        #     ) for i in self.inline_keyboard]
        # )
