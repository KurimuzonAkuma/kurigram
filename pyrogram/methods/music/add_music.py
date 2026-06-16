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

import os
from typing import BinaryIO, Callable, Optional, Union

import pyrogram
from pyrogram import StopTransmission, raw, utils
from pyrogram.errors import FilePartMissing
from pyrogram.file_id import FileType


class AddMusic:
    async def add_music(
        self: "pyrogram.Client",
        audio: Union[str, BinaryIO],
        duration: Optional[int] = 0,
        performer: Optional[str] = None,
        title: Optional[str] = None,
        thumb: Optional[Union[str, BinaryIO]] = None,
        file_name: Optional[str] = None,
        progress: Optional[Callable] = None,
        progress_args: Optional[tuple] = (),
    ):
        """Add an audio file to the beginning of the current user's saved music list.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            audio (``str`` | ``BinaryIO``):
                Audio file to save.
                Pass a file_id as string to reuse a file that already exists on Telegram servers,
                pass a file path as string to upload a local file, or
                pass a binary file-like object with its attribute ".name" set for in-memory uploads.

            duration (``int``, *optional*):
                Duration of the audio in seconds.

            performer (``str``, *optional*):
                Performer of the audio.

            title (``str``, *optional*):
                Title of the audio.

            thumb (``str`` | ``BinaryIO``, *optional*):
                Thumbnail of the audio.

            file_name (``str``, *optional*):
                File name of the audio.

            progress (``Callable``, *optional*):
                Pass a callback function to view the file transmission progress.

            progress_args (``tuple``, *optional*):
                Extra custom arguments for the progress callback function.

        Returns:
            ``bool`` | ``None``: On success, True is returned, otherwise, in case the upload is
            deliberately stopped with :meth:`~pyrogram.Client.stop_transmission`, None is returned.

        Example:
            .. code-block:: python

                await app.add_music("song.mp3", title="Title", performer="Artist")
        """
        file = None

        try:
            if isinstance(audio, str):
                if os.path.isfile(audio):
                    mime_type = self.guess_mime_type(audio) or "audio/mpeg"
                    if mime_type == "audio/ogg":
                        mime_type = "audio/opus"

                    thumb = await self.save_file(thumb)
                    file = await self.save_file(
                        audio, progress=progress, progress_args=progress_args
                    )

                    uploaded_media = await self.invoke(
                        raw.functions.messages.UploadMedia(
                            peer=raw.types.InputPeerSelf(),
                            media=raw.types.InputMediaUploadedDocument(
                                mime_type=mime_type,
                                file=file,
                                thumb=thumb,
                                attributes=[
                                    raw.types.DocumentAttributeAudio(
                                        duration=duration,
                                        performer=performer,
                                        title=title,
                                    ),
                                    raw.types.DocumentAttributeFilename(
                                        file_name=file_name or os.path.basename(audio)
                                    ),
                                ],
                            ),
                        )
                    )

                    media = raw.types.InputDocument(
                        id=uploaded_media.document.id,
                        access_hash=uploaded_media.document.access_hash,
                        file_reference=uploaded_media.document.file_reference,
                    )
                else:
                    media = utils.get_input_media_from_file_id(audio, FileType.AUDIO).id
            else:
                mime_type = self.guess_mime_type(file_name or audio.name) or "audio/mpeg"
                if mime_type == "audio/ogg":
                    mime_type = "audio/opus"

                thumb = await self.save_file(thumb)
                file = await self.save_file(
                    audio, progress=progress, progress_args=progress_args
                )

                uploaded_media = await self.invoke(
                    raw.functions.messages.UploadMedia(
                        peer=raw.types.InputPeerSelf(),
                        media=raw.types.InputMediaUploadedDocument(
                            mime_type=mime_type,
                            file=file,
                            thumb=thumb,
                            attributes=[
                                raw.types.DocumentAttributeAudio(
                                    duration=duration,
                                    performer=performer,
                                    title=title,
                                ),
                                raw.types.DocumentAttributeFilename(
                                    file_name=file_name or audio.name
                                ),
                            ],
                        ),
                    )
                )

                media = raw.types.InputDocument(
                    id=uploaded_media.document.id,
                    access_hash=uploaded_media.document.access_hash,
                    file_reference=uploaded_media.document.file_reference,
                )

            while True:
                try:
                    return await self.invoke(raw.functions.account.SaveMusic(id=media))
                except FilePartMissing as e:
                    await self.save_file(audio, file_id=file.id, file_part=e.value)
        except StopTransmission:
            return None
