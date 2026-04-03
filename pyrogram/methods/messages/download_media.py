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
from datetime import datetime
from typing import Union, Optional, Callable, BinaryIO, List, Literal, overload

import pyrogram
from pyrogram import types, utils
from pyrogram.file_id import FileId, FileType, PHOTO_TYPES

DEFAULT_DOWNLOAD_DIR = "downloads/"


class DownloadMedia:
    @overload
    async def download_media(
        self: "pyrogram.Client",
        message: Union[
            str,
            "types.Message",
            "types.Story",
            "types.Audio",
            "types.Document",
            "types.Photo",
            "types.Sticker",
            "types.Animation",
            "types.Video",
            "types.Voice",
            "types.VideoNote",
            "types.PaidMediaInfo",
            "types.Thumbnail",
            "types.StrippedThumbnail",
            "types.PaidMediaPreview",
        ],
        file_name: str = DEFAULT_DOWNLOAD_DIR,
        *,
        in_memory: bool = False,
        block: Literal[False],
        progress: Optional[Callable] = None,
        progress_args: tuple = (),
    ) -> None: ...

    @overload
    async def download_media(
        self: "pyrogram.Client",
        message: Union[
            str,
            "types.Message",
            "types.Story",
            "types.Audio",
            "types.Document",
            "types.Photo",
            "types.Sticker",
            "types.Animation",
            "types.Video",
            "types.Voice",
            "types.VideoNote",
            "types.PaidMediaInfo",
            "types.Thumbnail",
            "types.StrippedThumbnail",
            "types.PaidMediaPreview",
        ],
        file_name: str = DEFAULT_DOWNLOAD_DIR,
        *,
        in_memory: Literal[True],
        block: bool = True,
        progress: Optional[Callable] = None,
        progress_args: tuple = (),
    ) -> Union[BinaryIO, List[BinaryIO]]: ...

    @overload
    async def download_media(
        self: "pyrogram.Client",
        message: Union[
            str,
            "types.Message",
            "types.Story",
            "types.Audio",
            "types.Document",
            "types.Photo",
            "types.Sticker",
            "types.Animation",
            "types.Video",
            "types.Voice",
            "types.VideoNote",
            "types.PaidMediaInfo",
            "types.Thumbnail",
            "types.StrippedThumbnail",
            "types.PaidMediaPreview",
        ],
        file_name: str = DEFAULT_DOWNLOAD_DIR,
        *,
        in_memory: Literal[False],
        block: bool = True,
        progress: Optional[Callable] = None,
        progress_args: tuple = (),
    ) -> Union[str, List[str]]:
        ...

    async def download_media(
        self: "pyrogram.Client",
        message: Union[
            str,
            "types.Message",
            "types.Story",
            "types.Audio",
            "types.Document",
            "types.Photo",
            "types.Sticker",
            "types.Animation",
            "types.Video",
            "types.Voice",
            "types.VideoNote",
            "types.PaidMediaInfo",
            "types.Thumbnail",
            "types.StrippedThumbnail",
            "types.PaidMediaPreview"
        ],
        file_name: str = DEFAULT_DOWNLOAD_DIR,
        in_memory: bool = False,
        block: bool = True,
        progress: Optional[Callable] = None,
        progress_args: tuple = ()
    ) -> Union[str, BinaryIO, List[str], List[BinaryIO], None]:
        """Download the media from a message.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            message (``str`` | :obj:`~pyrogram.types.Message` | :obj:`~pyrogram.types.Story` | :obj:`~pyrogram.types.Audio` | :obj:`~pyrogram.types.Document` | :obj:`~pyrogram.types.Photo` | :obj:`~pyrogram.types.Sticker` | :obj:`~pyrogram.types.Animation` | :obj:`~pyrogram.types.Video` | :obj:`~pyrogram.types.Voice` | :obj:`~pyrogram.types.VideoNote` | :obj:`~pyrogram.types.PaidMediaInfo` | :obj:`~pyrogram.types.Thumbnail` | :obj:`~pyrogram.types.StrippedThumbnail` | :obj:`~pyrogram.types.PaidMediaPreview`):
                Pass a object containing the media, the media itself (message.audio, message.video, ...) or a file id
                as string.

            file_name (``str``, *optional*):
                A custom *file_name* to be used instead of the one provided by Telegram.
                By default, all files are downloaded in the *downloads* folder in your working directory.
                You can also specify a path for downloading files in a custom location: paths that end with "/"
                are considered directories. All non-existent folders will be created automatically.

            in_memory (``bool``, *optional*):
                Pass True to download the media in-memory.
                A binary file-like object with its attribute ".name" set will be returned.
                Defaults to False.

            block (``bool``, *optional*):
                Blocks the code execution until the file has been downloaded.
                Defaults to True.

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
            ``str`` | ``None`` | ``BinaryIO`` | ``List[str]`` | ``List[BinaryIO]``: On success, the absolute path of the downloaded file is returned,
            otherwise, in case the download failed or was deliberately stopped with
            :meth:`~pyrogram.Client.stop_transmission`, None is returned.
            Otherwise, in case ``in_memory=True``, a binary file-like object with its attribute ".name" set is returned.
            If the message contains multiple media (purchased paid media), a list of paths or binary file-like objects is returned.

        Raises:
            ValueError: if the message doesn't contain any downloadable media

        Example:
            Download media to file

            .. code-block:: python

                # Download from Message
                await app.download_media(message)

                # Download from file id
                await app.download_media(message.photo.file_id)

                # Download document of a message
                await app.download_media(message.document)

                # Keep track of the progress while downloading
                async def progress(current, total):
                    print(f"{current * 100 / total:.1f}%")

                await app.download_media(message, progress=progress)

            Download media in-memory

            .. code-block:: python

                file = await app.download_media(message, in_memory=True)

                file_name = file.name
                file_bytes = bytes(file.getbuffer())
        """
        available_media = ("audio", "document", "photo", "sticker", "animation", "video", "voice", "video_note",
                           "new_chat_photo", "paid_media")

        media = None

        if isinstance(message, types.Message) and message.media:
            story = message.story or message.reply_to_story

            for kind in available_media:
                if kind == "paid_media" and message.paid_media:
                    if isinstance(message.paid_media.media[0], types.PaidMediaPreview):
                        break

                    results = []

                    for item in message.paid_media.media:
                        result = await self.download_media(
                            item,
                            file_name=file_name,
                            in_memory=in_memory,
                            block=block,
                            progress=progress,
                            progress_args=progress_args,
                        )

                        if result:
                            results.append(result)

                    return results or None

                if story:
                    if self.me and self.me.is_bot:
                        raise ValueError("Bots can't see and download stories")

                    media = getattr(story, kind, None)
                else:
                    media = getattr(message, kind, None)

                if media is not None:
                    break
        elif isinstance(message, types.Story):
            if self.me and self.me.is_bot:
                raise ValueError("Bots can't see and download stories")

            media = getattr(message, message.media.value, None)
        elif isinstance(message, types.PaidMediaInfo) and not isinstance(message.media[0], types.PaidMediaPreview):
            results = []

            for item in message.media:
                result = await self.download_media(
                    item,
                    file_name=file_name,
                    in_memory=in_memory,
                    block=block,
                    progress=progress,
                    progress_args=progress_args,
                )

                if result:
                    results.append(result)

            return results or None
        elif isinstance(message, (types.StrippedThumbnail, types.PaidMediaPreview)):
            data = message.data if isinstance(message, types.StrippedThumbnail) else message.thumbnail.data

            thumb = utils.from_inline_bytes(
                utils.expand_inline_bytes(
                    data
                )
            )

            if in_memory:
                return thumb

            directory, file_name = os.path.split(file_name)
            file_name = file_name or thumb.name

            if not os.path.isabs(file_name):
                directory = self.PARENT_DIR / (directory or DEFAULT_DOWNLOAD_DIR)

            os.makedirs(directory, exist_ok=True) if not in_memory else None

            with open(os.path.join(directory, file_name), "wb") as file:
                file.write(thumb.getbuffer())

            return os.path.join(directory, file_name)
        elif isinstance(message, str):
            media = message
        elif hasattr(message, "file_id"):
            media = message

        if not media:
            raise ValueError("This message doesn't contain any downloadable media")

        if isinstance(media, str):
            file_id_str = media
        else:
            file_id_str = media.file_id

        file_id_obj = FileId.decode(file_id_str)

        file_type = file_id_obj.file_type
        media_file_name = getattr(media, "file_name", "")
        file_size = getattr(media, "file_size", 0)
        mime_type = getattr(media, "mime_type", "")
        date = getattr(media, "date", None)

        directory, file_name = os.path.split(file_name)
        file_name = file_name or media_file_name or ""

        if not os.path.isabs(file_name):
            directory = self.PARENT_DIR / (directory or DEFAULT_DOWNLOAD_DIR)

        if not file_name:
            guessed_extension = self.guess_extension(mime_type)

            if file_type in PHOTO_TYPES:
                extension = ".jpg"
            elif file_type == FileType.VOICE:
                extension = guessed_extension or ".ogg"
            elif file_type in (FileType.VIDEO, FileType.ANIMATION, FileType.VIDEO_NOTE):
                extension = guessed_extension or ".mp4"
            elif file_type == FileType.DOCUMENT:
                extension = guessed_extension or ".zip"
            elif file_type == FileType.STICKER:
                extension = guessed_extension or ".webp"
            elif file_type == FileType.AUDIO:
                extension = guessed_extension or ".mp3"
            else:
                extension = ".unknown"

            file_name = "{}_{}_{}{}".format(
                FileType(file_id_obj.file_type).name.lower(),
                (date or datetime.now()).strftime("%Y-%m-%d_%H-%M-%S"),
                self.rnd_id(),
                extension
            )

        downloader = self.handle_download(
            (file_id_obj, directory, file_name, in_memory, file_size, progress, progress_args)
        )

        if block:
            return await downloader
        else:
            self.loop.create_task(downloader)
