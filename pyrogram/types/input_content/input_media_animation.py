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


class InputMediaAnimation(InputMedia):
    """An animation file (GIF or H.264/MPEG-4 AVC video without sound) to be sent inside an album.

    Parameters:
        media (``str`` | ``BinaryIO``):
            Animation to send.
            Pass a file_id as string to send a file that exists on the Telegram servers or
            pass a file path as string to upload a new file that exists on your local machine or
            pass a binary file-like object with its attribute “.name” set for in-memory uploads or
            pass an HTTP URL as a string for Telegram to get an animation from the Internet.

        thumb (``str``, *optional*):
            Thumbnail of the animation file sent.
            The thumbnail should be in JPEG format and less than 200 KB in size.
            A thumbnail's width and height should not exceed 320 pixels.
            Thumbnails can't be reused and can be only uploaded as a new file.

        caption (``str``, *optional*):
            Caption of the animation to be sent, 0-1024 characters.
            If not specified, the original caption is kept. Pass "" (empty string) to remove the caption.

        parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
            List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

        width (``int``, *optional*):
            Animation width.

        height (``int``, *optional*):
            Animation height.

        duration (``int``, *optional*):
            Animation duration.

        has_spoiler (``bool``, *optional*):
            Pass True if the photo needs to be covered with a spoiler animation.

        file_name (``str``, *optional*):
            File name of the animation sent.
            Defaults to file's path basename.
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
        has_spoiler: Optional[bool] = None,
        file_name: Optional[str] = None,
    ):
        super().__init__(media, caption, parse_mode, caption_entities)

        self.thumb = thumb
        self.width = width
        self.height = height
        self.duration = duration
        self.has_spoiler = has_spoiler
        self.file_name = file_name

    async def write(
        self,
        *,
        client: "pyrogram.Client",
        chat_id: Optional[Union[int, str]] = None,
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
                        thumb=await client.save_file(self.thumb),
                        spoiler=self.has_spoiler,
                        attributes=[
                            raw.types.DocumentAttributeVideo(
                                supports_streaming=True,
                                duration=self.duration,
                                w=self.width,
                                h=self.height,
                            ),
                            raw.types.DocumentAttributeFilename(
                                file_name=utils.get_file_name(self.media, file_name=self.file_name),
                            ),
                            raw.types.DocumentAttributeAnimated(),
                        ],
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
            )

        if re.match("^https?://", self.media):
            return raw.types.InputMediaDocumentExternal(
                url=self.media,
                spoiler=self.has_spoiler,
            )

        return utils.get_input_media_from_file_id(
            self.media,
            FileType.ANIMATION,
            has_spoiler=self.has_spoiler,
        )
