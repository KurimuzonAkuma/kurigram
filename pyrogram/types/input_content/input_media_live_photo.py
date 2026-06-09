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

import io
import pathlib
import re
from typing import BinaryIO, Callable, List, Optional, Union

import pyrogram
from pyrogram import raw, utils
from pyrogram.file_id import FileType

from ... import enums
from ..messages_and_media import MessageEntity
from .input_media import InputMedia


class InputMediaLivePhoto(InputMedia):
    """Represents a live photo to be sent.

    Parameters:
        media (``str`` | ``BinaryIO``):
            Video of the live photo to send.
            Pass a file_id as string to send a video that exists on the Telegram servers or
            pass a file path as string to upload a new video that exists on your local machine or
            pass a binary file-like object with its attribute “.name” set for in-memory uploads or
            pass an HTTP URL as a string for Telegram to get a video from the Internet.

        photo (``str`` | ``BinaryIO``):
            The static photo to send.
            Pass a file_id as string to send a video that exists on the Telegram servers or
            pass a file path as string to upload a new video that exists on your local machine or
            pass a binary file-like object with its attribute “.name” set for in-memory uploads or
            pass an HTTP URL as a string for Telegram to get a video from the Internet.

        caption (``str``, *optional*):
            Caption of the video to be sent, 0-1024 characters.
            If not specified, the original caption is kept. Pass "" (empty string) to remove the caption.

        parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
            List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

        show_caption_above_media (``bool``, *optional*):
            Pass True, if the caption must be shown above the message media.

        has_spoiler (``bool``, *optional*):
            Pass True if the photo needs to be covered with a spoiler animation.
    """

    def __init__(
        self,
        media: Union[str, BinaryIO],
        photo: Union[str, BinaryIO],
        thumb: Optional[str] = None,
        caption: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        caption_entities: Optional[List[MessageEntity]] = None,
        show_caption_above_media: Optional[bool] = None,
        has_spoiler: Optional[bool] = None,

    ):
        super().__init__(media, caption, parse_mode, caption_entities)

        self.photo = photo
        self.thumb = thumb
        self.show_caption_above_media = show_caption_above_media
        self.has_spoiler = has_spoiler

    async def write(
        self,
        *,
        client: "pyrogram.Client",
        chat_id: Optional[Union[int, str]] = None,
        width: int = 0,
        height: int = 0,
        progress: Optional[Callable] = None,
        progress_args: tuple = (),
        **kwargs
    ) -> "raw.base.InputMedia":
        if chat_id is None:
            peer = raw.types.InputPeerSelf()
        else:
            peer = await client.resolve_peer(chat_id)

        if isinstance(self.media, io.BytesIO) or pathlib.Path(self.media).is_file():
            uploaded_media = await client.invoke(
                raw.functions.messages.UploadMedia(
                    peer=peer,
                    media=raw.types.InputMediaUploadedDocument(
                        mime_type=client.guess_mime_type(self.media) or "video/mp4",
                        file=await client.save_file(
                            self.media, progress=progress, progress_args=progress_args
                        ),
                        spoiler=self.has_spoiler,
                        attributes=[
                            raw.types.DocumentAttributeVideo(
                                duration=0,
                                w=width,
                                h=height,
                            ),
                        ],
                    ),
                ),
            )

            uploaded_photo = await client.invoke(
                raw.functions.messages.UploadMedia(
                    peer=peer,
                    media=raw.types.InputMediaUploadedPhoto(
                        video=await client.save_file(
                            self.media, progress=progress, progress_args=progress_args
                        ),
                        file=await client.save_file(
                            self.photo, progress=progress, progress_args=progress_args
                        ),
                        live_photo=True,
                        spoiler=self.has_spoiler,
                    ),
                )
            )

            return raw.types.InputMediaPhoto(
                id=raw.types.InputPhoto(
                    id=uploaded_photo.photo.id,
                    access_hash=uploaded_photo.photo.access_hash,
                    file_reference=uploaded_photo.photo.file_reference,
                ),
                live_photo=True,
                spoiler=self.has_spoiler,
                video=raw.types.InputDocument(
                    id=uploaded_media.document.id,
                    access_hash=uploaded_media.document.access_hash,
                    file_reference=uploaded_media.document.file_reference,
                )
            )

        return utils.get_input_media_from_file_id(
            self.photo,
            FileType.PHOTO,
            has_spoiler=self.has_spoiler,
            live_photo=True,
            live_photo_video_file_id=self.media,
        )
