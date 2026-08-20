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
import os
import re
from datetime import datetime
from typing import BinaryIO, Callable, List, Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils
from pyrogram.errors import FilePartMissing
from pyrogram.file_id import FileType

log = logging.getLogger(__name__)

class SendPhoto:
    async def send_photo(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        photo: Union[str, BinaryIO],
        caption: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        caption_entities: Optional[List["types.MessageEntity"]] = None,
        has_spoiler: Optional[bool] = None,
        ttl_seconds: Optional[int] = None,
        disable_notification: Optional[bool] = None,
        message_thread_id: Optional[int] = None,
        direct_messages_topic_id: Optional[int] = None,
        receiver_user_id: Optional[Union[int, str]] = None,
        callback_query_id: Optional[str] = None,
        effect_id: Optional[int] = None,
        show_caption_above_media: Optional[bool] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        schedule_date: Optional[datetime] = None,
        repeat_period: Optional[int] = None,
        protect_content: Optional[bool] = None,
        view_once: Optional[bool] = None,
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
        progress: Optional[Callable] = None,
        progress_args: tuple = (),

        reply_to_message_id: Optional[int] = None,
        reply_to_chat_id: Optional[Union[int, str]] = None,
        reply_to_story_id: Optional[int] = None,
        quote_text: Optional[str] = None,
        quote_entities: Optional[List["types.MessageEntity"]] = None,
        quote_offset: Optional[int] = None,
    ) -> Optional["types.Message"]:
        """Send photos.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            photo (``str`` | ``BinaryIO``):
                Photo to send.
                Pass a file_id as string to send a photo that exists on the Telegram servers,
                pass an HTTP URL as a string for Telegram to get a photo from the Internet,
                pass a file path as string to upload a new photo that exists on your local machine, or
                pass a binary file-like object with its attribute ".name" set for in-memory uploads.

            caption (``str``, *optional*):
                Photo caption, 0-1024 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
                List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

            has_spoiler (``bool``, *optional*):
                Pass True if the photo needs to be covered with a spoiler animation.

            ttl_seconds (``int``, *optional*):
                Self-Destruct Timer.
                If you set a timer, the photo will self-destruct in *ttl_seconds*
                seconds after it was viewed.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For forums only.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For direct chats only.only.

            receiver_user_id (``int`` | ``str``, *optional*):
                For outgoing ephemeral messages, unique identifier (int) or username (str) of the user who will receive the message.
                For group and supergroup chats only.
                It is not guaranteed that the user will receive the message, especially if they are offline.
                See `ephemeral message sending <https://core.telegram.org/bots/api#ephemeral-messages-and-commands>`__ for more details.

            callback_query_id (``str``, *optional*):
                For outgoing ephemeral messages, identifier of the callback query which triggered the message if any.

            effect_id (``int``, *optional*):
                Unique identifier of the message effect.
                For private chats only.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            repeat_period (``int``, *optional*):
                Period after which the message will be sent again in seconds.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            view_once (``bool``, *optional*):
                Self-Destruct Timer.
                If True, the photo will self-destruct after it was viewed.

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

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.
                The function must take *(current, total)* as positional arguments (look at Other Parameters below for a
                detailed description) and will be called back each time a new file chunk has been successfully
                transmitted.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.
                You can pass anything you need to be available in the progress callback scope; for example, a Message
                object or a Client instance in order to edit the message with the updated progress status.

        Other Parameters:
            current (``int``):
                The amount of bytes transmitted so far.

            total (``int``):
                The total size of the file.

            *args (``tuple``, *optional*):
                Extra custom arguments as defined in the ``progress_args`` parameter.
                You can either keep ``*args`` or add every single extra argument in your function signature.

        Returns:
            :obj:`~pyrogram.types.Message` | ``None``: On success, the sent photo message is returned, otherwise, in
            case the upload is deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned.

        Example:
            .. code-block:: python

                # Send photo by uploading from local file
                await app.send_photo("me", "photo.jpg")

                # Send photo by uploading from URL
                await app.send_photo("me", "https://example.com/example.jpg")

                # Add caption to a photo
                await app.send_photo("me", "photo.jpg", caption="Caption")

                # Send self-destructing photo
                await app.send_photo("me", "photo.jpg", ttl_seconds=10)

                # Send view-once photo
                await app.send_photo("me", "photo.jpg", view_once=True)
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

        file = None

        try:
            if isinstance(photo, str):
                if os.path.isfile(photo):
                    file = await self.save_file(photo, progress=progress, progress_args=progress_args)
                    media = raw.types.InputMediaUploadedPhoto(
                        file=file,
                        ttl_seconds=(1 << 31) - 1 if view_once else ttl_seconds,
                        spoiler=has_spoiler,
                    )
                elif re.match("^https?://", photo):
                    media = raw.types.InputMediaPhotoExternal(
                        url=photo,
                        ttl_seconds=(1 << 31) - 1 if view_once else ttl_seconds,
                        spoiler=has_spoiler
                    )
                else:
                    media = utils.get_input_media_from_file_id(photo, FileType.PHOTO, ttl_seconds=(1 << 31) - 1 if view_once else ttl_seconds, has_spoiler=has_spoiler)
            else:
                file = await self.save_file(photo, progress=progress, progress_args=progress_args)
                media = raw.types.InputMediaUploadedPhoto(
                    file=file,
                    ttl_seconds=(1 << 31) - 1 if view_once else ttl_seconds,
                    spoiler=has_spoiler
                )

            while True:
                try:
                    peer = await self.resolve_peer(chat_id)

                    if receiver_user_id:
                        rpc = raw.functions.ephemeral.SendMessage(
                            peer=peer,
                            receiver_id=await self.resolve_peer(receiver_user_id),
                            query_id=int(callback_query_id) if callback_query_id is not None else None,
                            media=media,
                            reply_to=await utils.get_reply_to(
                                self,
                                reply_parameters,
                                message_thread_id,
                                direct_messages_topic_id
                            ),
                            random_id=self.rnd_id(),
                            reply_markup=await reply_markup.write(self) if reply_markup else None,
                            **await utils.parse_text_entities(self, caption, parse_mode, caption_entities)
                        )
                    else:
                        rpc = raw.functions.messages.SendMedia(
                            peer=peer,
                            media=media,
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
                            schedule_repeat_period=repeat_period,
                            noforwards=protect_content,
                            allow_paid_floodskip=allow_paid_broadcast,
                            allow_paid_stars=paid_message_star_count,
                            suggested_post=suggested_post_parameters.write() if suggested_post_parameters else None,
                            reply_markup=await reply_markup.write(self) if reply_markup else None,
                            effect=effect_id,
                            **await utils.parse_text_entities(self, caption, parse_mode, caption_entities)
                        )

                    r = await self.invoke(rpc, business_connection_id=business_connection_id)
                except FilePartMissing as e:
                    await self.save_file(photo, file_id=file.id, file_part=e.file_part)
                else:
                    messages = await utils.parse_messages(client=self, messages=r)

                    return messages[0] if messages else None
        except pyrogram.StopTransmission:
            return None
