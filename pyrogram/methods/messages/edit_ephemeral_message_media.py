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

import logging
from typing import Union

import pyrogram
from pyrogram import raw, types, utils

log = logging.getLogger(__name__)


class EditEphemeralMessageMedia:
    async def edit_ephemeral_message_media(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        receiver_id: Union[int, str],
        message_id: int,
        media: "types.InputMedia",
        reply_markup: "types.InlineKeyboardMarkup" = None,
    ) -> "types.EphemeralMessage":
        """Edit the media of an ephemeral message.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            receiver_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the only user allowed to see this
                message.

            message_id (``int``):
                Identifier of the ephemeral message to edit.

            media (:obj:`~pyrogram.types.InputMedia`):
                One of the InputMedia objects describing an animation, audio, document, photo or
                video.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            :obj:`~pyrogram.types.EphemeralMessage`: On success, the edited message is returned.

        Example:
            .. code-block:: python

                from pyrogram import types

                await app.edit_ephemeral_message_media(
                    chat_id, receiver_id, message_id,
                    types.InputMediaPhoto("new_photo.jpg")
                )
        """
        r = await self.invoke(
            raw.functions.ephemeral.EditMessage(
                peer=await self.resolve_peer(chat_id),
                receiver_id=await utils.resolve_receiver(self, receiver_id),
                id=message_id,
                media=await media.write(self),
                reply_markup=await reply_markup.write(self) if reply_markup else None,
            )
        )

        return await utils.parse_ephemeral_message(self, r)
