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


class InputMediaVideo(InputMedia):
    """A video to be sent inside an album.

    It is intended to be used with :obj:`~pyrogram.Client.send_media_group` or :obj:`~pyrogram.Client.send_paid_media`.

    Parameters:
        media (``str`` | ``BinaryIO``):
            Video to send.
            Pass a file_id as string to send a video that exists on the Telegram servers or
            pass a file path as string to upload a new video that exists on your local machine or
            pass a binary file-like object with its attribute “.name” set for in-memory uploads or
            pass an HTTP URL as a string for Telegram to get a video from the Internet.

        thumb (``str``):
            Thumbnail of the video sent.
            The thumbnail should be in JPEG format and less than 200 KB in size.
            A thumbnail's width and height should not exceed 320 pixels.
            Thumbnails can't be reused and can be only uploaded as a new file.

        caption (``str``, *optional*):
            Caption of the video to be sent, 0-1024 characters.
            If not specified, the original caption is kept. Pass "" (empty string) to remove the caption.

        parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
            List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

        width (``int``, *optional*):
            Video width.

        height (``int``, *optional*):
            Video height.

        duration (``int``, *optional*):
            Video duration.

        file_name (``str``, *optional*):
            File name of the video sent.
            Defaults to file's path basename.

        supports_streaming (``bool``, *optional*):
            Pass True, if the uploaded video is suitable for streaming.

        has_spoiler (``bool``, *optional*):
            Pass True if the photo needs to be covered with a spoiler animation.

        no_sound (``bool``, *optional*):
            Pass True, if the uploaded video is a video message with no sound.
            Doesn't work for external links.

        video_start_timestamp (``int``, *optional*):
            Video startpoint, in seconds.

        video_cover (``str`` | ``BinaryIO``, *optional*):
            Video cover.
            Pass a file_id as string to attach a photo that exists on the Telegram servers,
            pass an HTTP URL as a string for Telegram to get a photo from the Internet,
            pass a file path as string to upload a new photo that exists on your local machine, or
            pass a binary file-like object with its attribute ".name" set for in-memory uploads.
    """

    def __init__(
        self,
        media: Union[str, BinaryIO],
        thumb: Optional[str] = None,
        caption: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        caption_entities: Optional[List[MessageEntity]] = None,
        width: int = 0,
        height: int = 0,
        duration: int = 0,
        file_name: Optional[str] = None,
        supports_streaming: bool = True,
        has_spoiler: Optional[bool] = None,
        no_sound: Optional[bool] = None,
        video_start_timestamp: Optional[int] = None,
        video_cover: Optional[Union[str, BinaryIO]] = None,
    ):
        super().__init__(media, caption, parse_mode, caption_entities)

        self.thumb = thumb
        self.width = width
        self.height = height
        self.duration = duration
        self.file_name = file_name
        self.supports_streaming = supports_streaming
        self.has_spoiler = has_spoiler
        self.no_sound = no_sound
        self.video_start_timestamp = video_start_timestamp
        self.video_cover = video_cover

    async def write(
        self,
        *,
        client: "pyrogram.Client",
        chat_id: Optional[Union[int, str]] = None,
        progress: Optional[Callable] = None,
        progress_args: tuple = (),
        ttl_seconds: Optional[int] = None,
        **kwargs
    ) -> "raw.base.InputMedia":
        if chat_id is None:
            peer = raw.types.InputPeerSelf()
        else:
            peer = await client.resolve_peer(chat_id)

        input_video_cover = None

        if self.video_cover is not None:
            if (
                isinstance(self.video_cover, io.BytesIO)
                or pathlib.Path(self.video_cover).is_file()
            ):
                uploaded_media = await client.invoke(
                    raw.functions.messages.UploadMedia(
                        peer=peer,
                        media=raw.types.InputMediaUploadedPhoto(
                            file=await client.save_file(self.video_cover)
                        ),
                    )
                )

                input_video_cover = raw.types.InputPhoto(
                    id=uploaded_media.photo.id,
                    access_hash=uploaded_media.photo.access_hash,
                    file_reference=uploaded_media.photo.file_reference,
                )
            elif re.match("^https?://", self.video_cover):
                uploaded_media = await client.invoke(
                    raw.functions.messages.UploadMedia(
                        peer=peer, media=raw.types.InputMediaPhotoExternal(url=self.video_cover)
                    )
                )

                input_video_cover = raw.types.InputPhoto(
                    id=uploaded_media.photo.id,
                    access_hash=uploaded_media.photo.access_hash,
                    file_reference=uploaded_media.photo.file_reference,
                )
            else:
                input_video_cover = utils.get_input_media_from_file_id(
                    self.video_cover, FileType.PHOTO
                ).id

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
                        thumb=await client.save_file(self.thumb),
                        video_cover=input_video_cover,
                        video_timestamp=self.video_start_timestamp,
                        nosound_video=self.no_sound,
                        attributes=[
                            raw.types.DocumentAttributeVideo(
                                supports_streaming=self.supports_streaming or None,
                                duration=self.duration,
                                w=self.width,
                                h=self.height,
                            ),
                            raw.types.DocumentAttributeFilename(
                                file_name=utils.get_file_name(self.media, file_name=self.file_name),
                            ),
                        ],
                        ttl_seconds=ttl_seconds,
                    ),
                ),
            )

            return raw.types.InputMediaDocument(
                id=raw.types.InputDocument(
                    id=uploaded_media.document.id,
                    access_hash=uploaded_media.document.access_hash,
                    file_reference=uploaded_media.document.file_reference,
                ),
                spoiler=self.has_spoiler,
                ttl_seconds=ttl_seconds,
                video_cover=input_video_cover,
                video_timestamp=self.video_start_timestamp,
            )

        if re.match("^https?://", self.media):
            return raw.types.InputMediaDocumentExternal(
                url=self.media,
                spoiler=self.has_spoiler,
                ttl_seconds=ttl_seconds,
                video_cover=input_video_cover,
                video_timestamp=self.video_start_timestamp,
            )

        return utils.get_input_media_from_file_id(
            self.media,
            FileType.VIDEO,
            has_spoiler=self.has_spoiler,
            ttl_seconds=ttl_seconds,
            video_cover=input_video_cover,
            video_start_timestamp=self.video_start_timestamp,
        )
