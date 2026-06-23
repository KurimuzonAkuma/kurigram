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
from typing import List, Optional

import pyrogram
from pyrogram import enums, raw, types, utils

log = logging.getLogger(__name__)

class EditInlineText:
    async def edit_inline_text(
        self: "pyrogram.Client",
        inline_message_id: str,
        text: Optional[str] = None,
        parse_mode: Optional["enums.ParseMode"] = None,
        link_preview_options: "types.LinkPreviewOptions" = None,
        entities: List["types.MessageEntity"] = None,
        rich_message: Optional["types.InputRichMessage"] = None,
        reply_markup: "types.InlineKeyboardMarkup" = None,
        disable_web_page_preview: bool = None,
    ) -> bool:
        """Edit the text of inline messages.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            inline_message_id (``str``):
                Identifier of the inline message.

            text (``str``, *optional*):
                New text of the message.
                Required if rich_message isn't specified.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in message text, which can be specified instead of *parse_mode*.

            link_preview_options (:obj:`~pyrogram.types.LinkPreviewOptions`, *optional*):
                Options used for link preview generation for the message.

            rich_message (:obj:`~pyrogram.types.InputRichMessage`, *optional*):
                New rich content of the message.
                Required if text isn't specified.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Bots only

                # Simple edit text
                await app.edit_inline_text(inline_message_id, "new text")

                # Take the same text message, remove the web page preview only
                from pyrogram import types

                await app.edit_inline_text(
                    inline_message_id, message.text,
                    link_preview_options=types.LinkPreviewOptions(is_disabled=True))
        """
        link_preview_options = link_preview_options or self.link_preview_options

        if disable_web_page_preview is not None:
            log.warning(
                "`disable_web_page_preview` is deprecated and will be removed in future updates. Use `link_preview_options` instead."
            )
            link_preview_options = types.LinkPreviewOptions(is_disabled=disable_web_page_preview)

        unpacked = utils.unpack_inline_message_id(inline_message_id)
        dc_id = unpacked.dc_id

        session = await self.get_session(dc_id, is_media=True)

        message = ""
        input_rich_message = None
        entities = None

        if text:
            message, entities = (
                await utils.parse_text_entities(self, text, parse_mode, entities)
            ).values()
        elif rich_message:
            input_rich_message = rich_message.write()
        else:
            raise ValueError("Either text or rich_message must be specified")

        return await session.invoke(
            raw.functions.messages.EditInlineBotMessage(
                id=unpacked,
                no_webpage=getattr(link_preview_options, "is_disabled", None) or None,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                message=message,
                entities=entities,
                rich_message=input_rich_message,
            ),
            sleep_threshold=self.sleep_threshold
        )
