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

from datetime import datetime
from typing import List, Optional

import pyrogram
from pyrogram import raw, utils
from pyrogram import types
from pyrogram.file_id import FileId, FileType, FileUniqueId, FileUniqueType, ThumbnailSource
from ..object import Object


class Animation(Object):
    """An animation file (GIF or H.264/MPEG-4 AVC video without sound).

    Parameters:
        file_id (``str``):
            Identifier for this file, which can be used to download or reuse the file.

        file_unique_id (``str``):
            Unique identifier for this file, which is supposed to be the same over time and for different accounts.
            Can't be used to download or reuse the file.

        width (``int``):
            Animation width as defined by sender.

        height (``int``):
            Animation height as defined by sender.

        duration (``int``):
            Duration of the animation in seconds as defined by sender.

        file_name (``str``, *optional*):
            Animation file name.

        mime_type (``str``, *optional*):
            Mime type of a file as defined by sender.

        file_size (``int``, *optional*):
            File size.

        date (:py:obj:`~datetime.datetime`, *optional*):
            Date the animation was sent.

        thumbs (List of :obj:`~pyrogram.types.Thumbnail`, *optional*):
            Animation thumbnails.
    """

    def __init__(
        self,
        *,
        client: Optional["pyrogram.Client"] = None,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        duration: int,
        file_name: Optional[str] = None,
        mime_type: Optional[str] = None,
        file_size: Optional[int] = None,
        date: Optional[datetime] = None,
        thumbs: Optional[List["types.Thumbnail"]] = None
    ):
        super().__init__(client)

        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size
        self.date = date
        self.width = width
        self.height = height
        self.duration = duration
        self.thumbs = thumbs

    async def add_to_gifs(
        self,
        unsave: bool = False
    ) -> bool:
        """Bound method *add_to_gifs* of :obj:`~pyrogram.types.Message`.

        .. include:: /_includes/usable-by/users.rst

        Use as a shortcut for:

        .. code-block:: python

            await app.add_to_gifs(message.animation.file_id)

        Parameters:
            unsave (``bool``, optional):
                Whether to remove the GIF from the list of saved GIFs. Defaults to ``False``.

        Returns:
            ``bool``: True on success.
        """
        return await self._client.add_to_gifs(self.file_id, unsave)

    @staticmethod
    def _parse(
        client,
        animation: "raw.types.Document",
        video_attributes: "raw.types.DocumentAttributeVideo",
        file_name: str
    ) -> "Animation":
        return Animation(
            file_id=FileId(
                file_type=FileType.ANIMATION,
                dc_id=animation.dc_id,
                media_id=animation.id,
                access_hash=animation.access_hash,
                file_reference=animation.file_reference
            ).encode(),
            file_unique_id=FileUniqueId(
                file_unique_type=FileUniqueType.DOCUMENT,
                media_id=animation.id
            ).encode(),
            width=getattr(video_attributes, "w", 0),
            height=getattr(video_attributes, "h", 0),
            duration=getattr(video_attributes, "duration", 0),
            mime_type=animation.mime_type,
            file_size=animation.size,
            file_name=file_name,
            date=utils.timestamp_to_datetime(animation.date),
            thumbs=types.Thumbnail._parse(client, animation),
            client=client
        )

    @staticmethod
    def _parse_chat_animation(
        client,
        video: "raw.types.Photo",
        file_name: str
    ) -> Optional["Animation"]:
        if isinstance(video, raw.types.Photo):
            if not video.video_sizes:
                return None

            videos: List[raw.types.VideoSize] = []

            for v in video.video_sizes:
                if isinstance(v, raw.types.VideoSize):
                    videos.append(v)

            videos.sort(key=lambda v: v.w * v.h)

            main = videos[-1]

            return Animation(
                file_id=FileId(
                    file_type=FileType.PHOTO,
                    dc_id=video.dc_id,
                    media_id=video.id,
                    access_hash=video.access_hash,
                    file_reference=video.file_reference,
                    thumbnail_source=ThumbnailSource.THUMBNAIL,
                    thumbnail_file_type=FileType.PHOTO,
                    thumbnail_size=main.type,
                    volume_id=0,
                    local_id=0
                ).encode(),
                file_unique_id=FileUniqueId(
                    file_unique_type=FileUniqueType.DOCUMENT,
                    media_id=video.id
                ).encode(),
                width=main.w,
                height=main.h,
                duration=0,
                file_size=main.size,
                date=utils.timestamp_to_datetime(video.date),
                file_name=file_name,
                mime_type="video/mp4",
                client=client
            )
