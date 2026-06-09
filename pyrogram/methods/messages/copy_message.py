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
from typing import TYPE_CHECKING, List, Optional, Union

if TYPE_CHECKING:
    import pyrogram
    from pyrogram import enums, types

log = logging.getLogger(__name__)


class CopyMessage:
    async def copy_message(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        from_chat_id: Union[int, str],
        message_id: int,
        caption: Optional[str] = None,
        parse_mode: Optional["enums.ParseMode"] = None,
        caption_entities: Optional[List["types.MessageEntity"]] = None,
        disable_notification: Optional[bool] = None,
        message_thread_id: Optional[int] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        schedule_date: Optional[datetime] = None,
        protect_content: Optional[bool] = None,
        has_spoiler: Optional[bool] = None,
        show_caption_above_media: Optional[bool] = None,
        business_connection_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        paid_message_star_count: Optional[int] = None,
        reply_markup: Optional[
            Union[
                "types.InlineKeyboardMarkup",
                "types.ReplyKeyboardMarkup",
                "types.ReplyKeyboardRemove",
                "types.ForceReply",
            ]
        ] = object,

        reply_to_chat_id: Optional[Union[int, str]] = None,
        reply_to_message_id: Optional[int] = None,
        quote_text: Optional[str] = None,
        quote_entities: Optional[List["types.MessageEntity"]] = None,
    ) -> "types.Message":
        """Copy messages of any kind.

        The method is analogous to the method :meth:`~Client.forward_messages`, but the copied message doesn't have a
        link to the original message.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            from_chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the source chat where the original message was sent.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_id (``int``):
                Message identifier in the chat specified in *from_chat_id*.

            caption (``str``, *optional*):
                New caption for media, 0-1024 characters after entities parsing.
                If not specified, the original caption is kept.
                Pass "" (empty string) to remove the caption.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the new caption, which can be specified instead of *parse_mode*.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For supergroups only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

            allow_paid_broadcast (``bool``, *optional*):
                If True, you will be allowed to send up to 1000 messages per second.
                Ignoring broadcasting limits for a fee of 0.1 Telegram Stars per message.
                The relevant Stars will be withdrawn from the bot's balance.
                For bots only.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay to send the messages.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.
                If not specified, the original reply markup is kept.
                Pass None to remove the reply markup.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the copied message is returned.

        Example:
            .. code-block:: python

                # Copy a message
                await app.copy_message(to_chat, from_chat, 123)

        """
        message: types.Message = await self.get_messages(
            chat_id=from_chat_id, message_ids=message_id
        )

        return await message.copy(
            chat_id=chat_id,
            caption=caption,
            parse_mode=parse_mode,
            caption_entities=caption_entities,
            disable_notification=disable_notification,
            message_thread_id=message_thread_id,
            reply_parameters=reply_parameters,
            schedule_date=schedule_date,
            protect_content=protect_content,
            has_spoiler=has_spoiler,
            show_caption_above_media=show_caption_above_media,
            business_connection_id=business_connection_id,
            allow_paid_broadcast=allow_paid_broadcast,
            paid_message_star_count=paid_message_star_count,
            reply_markup=reply_markup,
            reply_to_chat_id=reply_to_chat_id,
            reply_to_message_id=reply_to_message_id,
            quote_text=quote_text,
            quote_entities=quote_entities,
        )
