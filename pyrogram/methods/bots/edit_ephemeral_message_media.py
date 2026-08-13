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


class EditEphemeralMessageMedia:
    async def edit_ephemeral_message_media(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        receiver_user_id: Union[int, str],
        ephemeral_message_id: int,
        media: "types.InputMedia",
        reply_markup: Optional["types.InlineKeyboardMarkup"] = None,
    ) -> Optional["types.Message"]:
        """Use this method to edit the media of an ephemeral message.
        Note that it is not guaranteed that the user will receive the message edit event, especially if they are offline.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            receiver_user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the user who received the message.

            ephemeral_message_id (``int``):
                Identifier of the ephemeral message to edit.

            media (:obj:`~pyrogram.types.InputMedia`):
                One of the InputMedia objects describing an animation, audio, document, photo or video.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

            file_name (``str``, *optional*):
                File name of the media to be sent. Not applicable to photos.
                Defaults to file's path basename.

        Returns:
            :obj:`~pyrogram.types.Message` | ``None``: On success, the edited message is returned,
            otherwise, in case the server answered with no message, None is returned.

        Example:
            .. code-block:: python

                from pyrogram.types import InputMediaPhoto, InputMediaVideo, InputMediaAudio

                # Replace the current media with a local photo
                await app.edit_ephemeral_message_media(chat_id, receiver_user_id, message_id,
                    InputMediaPhoto("new_photo.jpg"))

                # Replace the current media with a local video
                await app.edit_ephemeral_message_media(chat_id, receiver_user_id, message_id,
                    InputMediaVideo("new_video.mp4"))

                # Replace the current media with a local audio
                await app.edit_ephemeral_message_media(chat_id, receiver_user_id, message_id,
                    InputMediaAudio("new_audio.mp3"))
        """
        caption = media.caption
        parse_mode = media.parse_mode
        caption_entities = media.caption_entities

        message, entities = None, None

        if caption is not None:
            message, entities = (
                await utils.parse_text_entities(self, caption, parse_mode, caption_entities)
            ).values()

        if not isinstance(
            media,
            (
                types.InputMediaPhoto,
                types.InputMediaVideo,
                types.InputMediaAudio,
                types.InputMediaAnimation,
                types.InputMediaDocument,
            ),
        ):
            raise ValueError(f"Unsupported media type {type(media)}")

        r = await self.invoke(
            raw.functions.ephemeral.EditMessage(
                peer=await self.resolve_peer(chat_id),
                receiver_id=await self.resolve_peer(receiver_user_id),
                id=ephemeral_message_id,
                media=await media.write(client=self),
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                message=message,
                entities=entities,
            )
        )

        messages = await utils.parse_messages(client=self, messages=r)

        return messages[0] if messages else None
