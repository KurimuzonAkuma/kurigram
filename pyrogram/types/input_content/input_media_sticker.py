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
from typing import BinaryIO, Callable, Optional, Union

import pyrogram
from pyrogram import raw, utils
from pyrogram.file_id import FileType

from .input_media import InputMedia


class InputMediaSticker(InputMedia):
    """A sticker to be attached.

    Parameters:
        media (``str`` | ``BinaryIO``):
            Sticker to send.
            Pass a file_id as string to send a file that exists on the Telegram servers or
            pass a file path as string to upload a new file that exists on your local machine or
            pass a binary file-like object with its attribute “.name” set for in-memory uploads or
            pass an HTTP URL as a string for Telegram to get the webp file from the Internet.

        emoji (``str``, *optional*):
            Emoji associated with this sticker.
    """

    def __init__(
        self,
        media: Union[str, BinaryIO],
        emoji: str = "",
    ) -> None:
        super().__init__(media)

        self.emoji = emoji

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
                        mime_type=client.guess_mime_type(self.media) or "image/webp",
                        file=await client.save_file(
                            self.media, progress=progress, progress_args=progress_args
                        ),
                        attributes=[
                            raw.types.DocumentAttributeFilename(
                                file_name=utils.get_file_name(self.media),
                            ),
                            raw.types.DocumentAttributeSticker(
                                alt=self.emoji, stickerset=raw.types.InputStickerSetEmpty()
                            ),
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
            )

        if re.match("^https?://", self.media):
            return raw.types.InputMediaDocumentExternal(
                url=self.media,
            )

        return utils.get_input_media_from_file_id(self.media, FileType.STICKER)
