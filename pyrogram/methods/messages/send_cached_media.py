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

class SendCachedMedia:
    async def send_cached_media(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        file_id: str,
        caption: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        caption_entities: Optional[List["types.MessageEntity"]] = None,
        disable_notification: Optional[bool] = None,
        message_thread_id: Optional[int] = None,
        direct_messages_topic_id: Optional[int] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        schedule_date: Optional[datetime] = None,
        protect_content: Optional[bool] = None,
        has_spoiler: Optional[bool] = None,
        effect_id: Optional[int] = None,
        show_caption_above_media: Optional[bool] = None,
        business_connection_id: Optional[str] = None,
        allow_paid_broadcast: Optional[bool] = None,
        paid_message_star_count: Optional[int] = None,
        suggested_post_parameters: Optional["types.SuggestedPostParameters"] = None,
        reply_markup: Optional[Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ]] = None,

        reply_to_message_id: Optional[int] = None,
        reply_to_chat_id: Optional[Union[int, str]] = None,
        reply_to_story_id: Optional[int] = None,
        quote_text: Optional[str] = None,
        quote_offset: Optional[int] = None,
        quote_entities: Optional[List["types.MessageEntity"]] = None,
    ) -> Optional["types.Message"]:
        """Send any media stored on the Telegram servers using a file_id.

        This convenience method works with any valid file_id only.
        It does the same as calling the relevant method for sending media using a file_id, thus saving you from the
        hassle of using the correct method for the media the file_id is pointing to.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            file_id (``str``):
                Media to send.
                Pass a file_id as string to send a media that exists on the Telegram servers.

            caption (``str``, *optional*):
                Media caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For direct chats only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            has_spoiler (``bool``, *optional*):
                True, if the message media is covered by a spoiler animation.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

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

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent media message is returned.

        Example:
            .. code-block:: python

                await app.send_cached_media("me", file_id)
        """
        if any(
            (
                reply_to_message_id is not None,
                reply_to_chat_id is not None,
                reply_to_story_id is not None,
                quote_text is not None,
                quote_entities is not None,
                quote_offset is not None,
            )
        ):
            if reply_to_message_id is not None:
                log.warning(
                    "`reply_to_message_id` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if reply_to_chat_id is not None:
                log.warning(
                    "`reply_to_chat_id` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if reply_to_story_id is not None:
                log.warning(
                    "`reply_to_story_id` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if quote_text is not None:
                log.warning(
                    "`quote_text` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if quote_entities is not None:
                log.warning(
                    "`quote_entities` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            if quote_offset is not None:
                log.warning(
                    "`quote_offset` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
                )

            reply_parameters = types.ReplyParameters(
                message_id=reply_to_message_id,
                chat_id=reply_to_chat_id,
                story_id=reply_to_story_id,
                quote=quote_text,
                quote_parse_mode=parse_mode,
                quote_entities=quote_entities,
                quote_position=quote_offset
            )

        r = await self.invoke(
            raw.functions.messages.SendMedia(
                peer=await self.resolve_peer(chat_id),
                media=utils.get_input_media_from_file_id(file_id, has_spoiler=has_spoiler),
                silent=disable_notification or None,
                invert_media=show_caption_above_media,
                reply_to=await utils.get_reply_to(
                    self,
                    reply_parameters,
                    message_thread_id,
                    direct_messages_topic_id
                ),
                random_id=self.rnd_id(),
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                noforwards=protect_content,
                allow_paid_floodskip=allow_paid_broadcast,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                effect=effect_id,
                allow_paid_stars=paid_message_star_count,
                suggested_post=suggested_post_parameters.write() if suggested_post_parameters else None,
                **await utils.parse_text_entities(self, caption, parse_mode, caption_entities)
            ),
            business_connection_id=business_connection_id
        )

        messages = await utils.parse_messages(client=self, messages=r)

        return messages[0] if messages else None
