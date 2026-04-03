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
from typing import List, Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils
from pyrogram.file_id import FileType

log = logging.getLogger(__name__)


class SendPaidMedia:
    # TODO: Add progress parameter
    async def send_paid_media(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        stars_amount: int,
        media: List[Union[
            "types.InputMediaPhoto",
            "types.InputMediaVideo",
        ]],
        caption: str = "",
        payload: str = None,
        parse_mode: Optional["enums.ParseMode"] = None,
        caption_entities: List["types.MessageEntity"] = None,
        disable_notification: bool = None,
        direct_messages_topic_id: int = None,
        reply_parameters: "types.ReplyParameters" = None,
        suggested_post_parameters: "types.SuggestedPostParameters" = None,
        schedule_date: datetime = None,
        protect_content: bool = None,
        show_caption_above_media: bool = None,
        business_connection_id: str = None,

        reply_to_message_id: int = None,
        quote_text: str = None,
        quote_entities: List["types.MessageEntity"] = None,
        quote_offset: int = None,
    ) -> List["types.Message"]:
        """Send a group or one paid photo/video.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            stars_amount (``int``):
                The number of Telegram Stars that must be paid to buy access to the media.

            media (List of :obj:`~pyrogram.types.InputMediaPhoto`, :obj:`~pyrogram.types.InputMediaVideo`):
                A list describing photos and videos to be sent, must include 1–10 items.

            caption (``str``, *optional*):
                Media caption, 0-1024 characters after entities parsing.

            invoice_payload (``str``):
                Bot-defined invoice payload, 1-128 bytes. This will not be displayed to the user, use for your internal processes.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            disable_notification (``bool``, *optional*):
                Sends the message silently.
                Users will receive a notification with no sound.

            direct_messages_topic_id (``int``, *optional*):
                Unique identifier of the topic in a channel direct messages chat administered by the current user.
                For directs only only.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Describes reply parameters for the message that is being sent.

            suggested_post_parameters (:obj:`~pyrogram.types.SuggestedPostParameters`, *optional*):
                Information about the suggested post.

            schedule_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the message will be automatically sent.

            protect_content (``bool``, *optional*):
                Protects the contents of the sent message from forwarding and saving.

            show_caption_above_media (``bool``, *optional*):
                Pass True, if the caption must be shown above the message media.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection on behalf of which the message will be sent.

        Returns:
            List of :obj:`~pyrogram.types.Message`: On success, a list of messages is returned.

        Example:
            .. code-block:: python

                from pyrogram.types import InputMediaPhoto, InputMediaVideo

                await app.send_paid_media(
                    chat_id,
                    stars_amount=50,
                    caption="Look at this!",
                    media=[
                        InputMediaPhoto("photo1.jpg"),
                        InputMediaPhoto("photo2.jpg"),
                        InputMediaVideo("video.mp4")
                    ]
                )
        """
        if any(
            (
                reply_to_message_id is not None,
                quote_text is not None,
                quote_entities is not None,
                quote_offset is not None,
            )
        ):
            if reply_to_message_id is not None:
                log.warning(
                    "`reply_to_message_id` is deprecated and will be removed in future updates. Use `reply_parameters` instead."
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
                quote=quote_text,
                quote_parse_mode=parse_mode,
                quote_entities=quote_entities,
                quote_position=quote_offset
            )

        multi_media = []
        peer = await self.resolve_peer(chat_id)

        for i in media:
            if isinstance(i, types.InputMediaPhoto):
                if isinstance(i.media, str):
                    if os.path.isfile(i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                peer=peer,
                                media=raw.types.InputMediaUploadedPhoto(
                                    file=await self.save_file(i.media),
                                    spoiler=i.has_spoiler
                                ),
                            )
                        )

                        media = raw.types.InputMediaPhoto(
                            id=raw.types.InputPhoto(
                                id=media.photo.id,
                                access_hash=media.photo.access_hash,
                                file_reference=media.photo.file_reference
                            ),
                            spoiler=i.has_spoiler
                        )
                    elif re.match("^https?://", i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaPhotoExternal(
                                    url=i.media
                                )
                            )
                        )
                    else:
                        media = utils.get_input_media_from_file_id(i.media, FileType.PHOTO, has_spoiler=i.has_spoiler)
                else:
                    media = await self.invoke(
                        raw.functions.messages.UploadMedia(
                            peer=peer,
                            media=raw.types.InputMediaUploadedPhoto(
                                file=await self.save_file(i.media),
                                spoiler=i.has_spoiler
                            ),
                        )
                    )

                    media = raw.types.InputMediaPhoto(
                        id=raw.types.InputPhoto(
                            id=media.photo.id,
                            access_hash=media.photo.access_hash,
                            file_reference=media.photo.file_reference
                        ),
                        spoiler=i.has_spoiler
                    )
            elif isinstance(i, types.InputMediaVideo):
                vcover_file = None
                vcover_media = None

                if i.video_cover is not None:
                    if isinstance(i.video_cover, str):
                        if os.path.isfile(i.video_cover):
                            vcover_media = await self.invoke(
                                raw.functions.messages.UploadMedia(
                                    peer=peer,
                                    media=raw.types.InputMediaUploadedPhoto(
                                        file=await self.save_file(i.video_cover)
                                    )
                                )
                            )
                        elif re.match("^https?://", i.video_cover):
                            vcover_media = await self.invoke(
                                raw.functions.messages.UploadMedia(
                                    peer=peer,
                                    media=raw.types.InputMediaPhotoExternal(
                                        url=i.video_cover
                                    )
                                )
                            )
                        else:
                            vcover_file = utils.get_input_media_from_file_id(i.video_cover, FileType.PHOTO).id
                    else:
                        vcover_media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                peer=peer,
                                media=raw.types.InputMediaUploadedPhoto(
                                    file=await self.save_file(i.video_cover)
                                )
                            )
                        )

                    if vcover_media:
                        vcover_file = raw.types.InputPhoto(
                            id=vcover_media.photo.id,
                            access_hash=vcover_media.photo.access_hash,
                            file_reference=vcover_media.photo.file_reference
                        )

                if isinstance(i.media, str):
                    if os.path.isfile(i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                peer=peer,
                                media=raw.types.InputMediaUploadedDocument(
                                    file=await self.save_file(i.media),
                                    thumb=await self.save_file(i.thumb),
                                    spoiler=i.has_spoiler,
                                    mime_type=self.guess_mime_type(i.media) or "video/mp4",
                                    nosound_video=True,
                                    video_cover=vcover_file,
                                    video_timestamp=i.video_start_timestamp,
                                    attributes=[
                                        raw.types.DocumentAttributeVideo(
                                            supports_streaming=i.supports_streaming or None,
                                            duration=i.duration,
                                            w=i.width,
                                            h=i.height
                                        ),
                                        raw.types.DocumentAttributeFilename(file_name=os.path.basename(i.media))
                                    ]
                                ),
                            )
                        )

                        media = raw.types.InputMediaDocument(
                            id=raw.types.InputDocument(
                                id=media.document.id,
                                access_hash=media.document.access_hash,
                                file_reference=media.document.file_reference,
                            ),
                            spoiler=i.has_spoiler,
                            video_cover=vcover_file,
                            video_timestamp=i.video_start_timestamp
                        )
                    elif re.match("^https?://", i.media):
                        media = await self.invoke(
                            raw.functions.messages.UploadMedia(
                                peer=await self.resolve_peer(chat_id),
                                media=raw.types.InputMediaDocumentExternal(
                                    url=i.media,
                                    video_cover=vcover_file,
                                    video_timestamp=i.video_start_timestamp
                                )
                            )
                        )
                    else:
                        media = utils.get_input_media_from_file_id(
                            i.media,
                            FileType.VIDEO,
                            has_spoiler=i.has_spoiler,
                            video_cover=vcover_file,
                            video_start_timestamp=i.video_start_timestamp
                        )
                else:
                    media = await self.invoke(
                        raw.functions.messages.UploadMedia(
                            peer=peer,
                            media=raw.types.InputMediaUploadedDocument(
                                file=await self.save_file(i.media),
                                thumb=await self.save_file(i.thumb),
                                spoiler=i.has_spoiler,
                                mime_type=self.guess_mime_type(getattr(i.media, "name", "video.mp4")) or "video/mp4",
                                nosound_video=True,
                                video_cover=vcover_file,
                                video_timestamp=i.video_start_timestamp,
                                attributes=[
                                    raw.types.DocumentAttributeVideo(
                                        supports_streaming=i.supports_streaming or None,
                                        duration=i.duration,
                                        w=i.width,
                                        h=i.height
                                    ),
                                    raw.types.DocumentAttributeFilename(file_name=getattr(i.media, "name", "video.mp4"))
                                ]
                            ),
                        )
                    )

                    media = raw.types.InputMediaDocument(
                        id=raw.types.InputDocument(
                            id=media.document.id,
                            access_hash=media.document.access_hash,
                            file_reference=media.document.file_reference
                        ),
                        video_cover=vcover_file,
                        video_timestamp=i.video_start_timestamp,
                        spoiler=i.has_spoiler
                    )
            else:
                raise ValueError(f"{i.__class__.__name__} is not a supported type for send_paid_media")

            multi_media.append(media)

        r = await self.invoke(
            raw.functions.messages.SendMedia(
                peer=peer,
                media=raw.types.InputMediaPaidMedia(
                    stars_amount=stars_amount,
                    extended_media=multi_media,
                    payload=payload
                ),
                silent=disable_notification or None,
                reply_to=await utils.get_reply_to(
                    self,
                    reply_parameters,
                    direct_messages_topic_id
                ),
                random_id=self.rnd_id(),
                schedule_date=utils.datetime_to_timestamp(schedule_date),
                noforwards=protect_content,
                invert_media=show_caption_above_media,
                suggested_post=suggested_post_parameters.write() if suggested_post_parameters else None,
                **await utils.parse_text_entities(self, caption, parse_mode, caption_entities)
            ),
            sleep_threshold=60,
            business_connection_id=business_connection_id
        )

        return await utils.parse_messages(client=self, messages=r)
