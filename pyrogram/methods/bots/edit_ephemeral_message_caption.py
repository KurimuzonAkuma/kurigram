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

from typing import TYPE_CHECKING, List, Optional, Union

if TYPE_CHECKING:
    import pyrogram
    from pyrogram import enums, types


class EditEphemeralMessageCaption:
    async def edit_ephemeral_message_caption(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        receiver_user_id: Union[int, str],
        ephemeral_message_id: int,
        caption: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        caption_entities: Optional[List["types.MessageEntity"]] = None,
        reply_markup: Optional["types.InlineKeyboardMarkup"] = None,
    ) -> "types.Message":
        """Use this method to edit the caption of an ephemeral message.
        Note that it is not guaranteed that the user will receive the message edit event, especially if they are offline.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            receiver_user_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the user who received the message.

            ephemeral_message_id (``int``):
                Identifier of the ephemeral message to edit.

            caption (``str``, *optional*):
                New caption of the message, 0-1024 characters after entities parsing.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the edited message is returned.

        Example:
            .. code-block:: python

                await app.edit_ephemeral_message_caption(chat_id, message_id, receiver_user_id, "new media caption")
        """
        link_preview_options = self.link_preview_options

        return await self.edit_ephemeral_message_text(
            chat_id=chat_id,
            receiver_user_id=receiver_user_id,
            ephemeral_message_id=ephemeral_message_id,
            text=caption,
            parse_mode=parse_mode,
            entities=caption_entities,
            link_preview_options=link_preview_options,
            reply_markup=reply_markup
        )
