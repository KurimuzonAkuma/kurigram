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


class InputMediaPhoto(InputMedia):
    """A photo to be sent inside an album.
    It is intended to be used with :obj:`~pyrogram.Client.send_media_group`.

    Parameters:
        media (``str`` | ``BinaryIO``):
            Photo to send.
            Pass a file_id as string to send a photo that exists on the Telegram servers or
            pass a file path as string to upload a new photo that exists on your local machine or
            pass a binary file-like object with its attribute “.name” set for in-memory uploads or
            pass an HTTP URL as a string for Telegram to get a photo from the Internet.

        caption (``str``, *optional*):
            Caption of the photo to be sent, 0-1024 characters.
            If not specified, the original caption is kept. Pass "" (empty string) to remove the caption.

        parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        caption_entities (List of :obj:`~pyrogram.types.MessageEntity`):
            List of special entities that appear in the caption, which can be specified instead of *parse_mode*.

        has_spoiler (``bool``, *optional*):
            Pass True if the photo needs to be covered with a spoiler animation.
    """

    def __init__(
        self,
        media: Union[str, BinaryIO],
        caption: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        caption_entities: Optional[List[MessageEntity]] = None,
        has_spoiler: Optional[bool] = None
    ):
        super().__init__(media, caption, parse_mode, caption_entities)

        self.has_spoiler = has_spoiler

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
        # TODO: add support for live photos and maybe move ttl_seconds to class param

        if chat_id is None:
            peer = raw.types.InputPeerSelf()
        else:
            peer = await client.resolve_peer(chat_id)

        if isinstance(self.media, io.BytesIO) or pathlib.Path(self.media).is_file():
            uploaded_media = await client.invoke(
                raw.functions.messages.UploadMedia(
                    peer=peer,
                    media=raw.types.InputMediaUploadedPhoto(
                        file=await client.save_file(
                            self.media, progress=progress, progress_args=progress_args
                        ),
                        spoiler=self.has_spoiler,
                        ttl_seconds=ttl_seconds,
                    ),
                )
            )

            return raw.types.InputMediaPhoto(
                id=raw.types.InputPhoto(
                    id=uploaded_media.photo.id,
                    access_hash=uploaded_media.photo.access_hash,
                    file_reference=uploaded_media.photo.file_reference,
                ),
                spoiler=self.has_spoiler,
                ttl_seconds=ttl_seconds,
            )

        if re.match("^https?://", self.media):
            return raw.types.InputMediaPhotoExternal(
                url=self.media,
                spoiler=self.has_spoiler,
                ttl_seconds=ttl_seconds,
            )

        return utils.get_input_media_from_file_id(
            self.media,
            FileType.PHOTO,
            has_spoiler=self.has_spoiler,
            ttl_seconds=ttl_seconds,
        )
