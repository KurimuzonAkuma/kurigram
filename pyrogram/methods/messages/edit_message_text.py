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
from datetime import datetime
from typing import List, Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils

log = logging.getLogger(__name__)


class EditMessageText:
    async def edit_message_text(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        text: str,
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: List["types.MessageEntity"] = None,
        link_preview_options: "types.LinkPreviewOptions" = None,
        schedule_date: datetime = None,
        business_connection_id: str = None,
        reply_markup: "types.InlineKeyboardMarkup" = None,

        show_caption_above_media: bool = None,
        disable_web_page_preview: bool = None,
    ) -> "types.Message":
        """Edit the text of messages.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_id (``int``):
                Message identifier in the chat specified in chat_id.

            text (``str``):
                New text of the message.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in message text, which can be specified instead of *parse_mode*.

            link_preview_options (:obj:`~pyrogram.types.LinkPreviewOptions`, *optional*):
                Options used for link preview generation for the message.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the edited message is returned.

        Example:
            .. code-block:: python

                # Simple edit text
                await app.edit_message_text(chat_id, message_id, "new text")

                # Take the same text message, remove the web page preview only
                from pyrogram import types

                await app.edit_message_text(
                    chat_id, message_id, message.text,
                    link_preview_options=types.LinkPreviewOptions(is_disabled=True))
        """
        if any(
            (
                disable_web_page_preview is not None,
                show_caption_above_media is not None,
            )
        ):
            if disable_web_page_preview is not None:
                log.warning(
                    "`disable_web_page_preview` is deprecated and will be removed in future updates. Use `link_preview_options` instead."
                )

            if show_caption_above_media is not None:
                log.warning(
                    "`show_caption_above_media` is deprecated and will be removed in future updates. Use `link_preview_options` instead."
                )

            link_preview_options = types.LinkPreviewOptions(
                is_disabled=disable_web_page_preview,
                show_above_text=show_caption_above_media
            )

        link_preview_options = link_preview_options or self.link_preview_options

        r = await self.invoke(
            raw.functions.messages.EditMessage(
                peer=await self.resolve_peer(chat_id),
                id=message_id,
                no_webpage=getattr(link_preview_options, "is_disabled", None),
                invert_media=getattr(link_preview_options, "show_above_text", None),
                media=(
                    raw.types.InputMediaWebPage(
                        url=link_preview_options.url,
                        force_large_media=link_preview_options.prefer_large_media,
                        force_small_media=link_preview_options.prefer_small_media,
                        optional=True
                    )
                    if link_preview_options and link_preview_options.url
                    else None
                ),
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                **await utils.parse_text_entities(self, text, parse_mode, entities)
            ),
            business_connection_id=business_connection_id
        )

        for i in r.updates:
            if isinstance(i, (raw.types.UpdateEditMessage, raw.types.UpdateEditChannelMessage)):
                return await types.Message._parse(
                    self, i.message,
                    {i.id: i for i in r.users},
                    {i.id: i for i in r.chats}
                )
