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

from typing import TYPE_CHECKING, Optional

from pyrogram.file_id import FileId, FileType, FileUniqueId, FileUniqueType

from ..object import Object

if TYPE_CHECKING:
    import pyrogram
    from pyrogram import raw


class LivePhoto(Object):
    """A live photo.

    Parameters:
        file_id (``str``):
            Identifier for this file, which can be used to download or reuse the file.

        file_unique_id (``str``):
            Unique identifier for this file, which is supposed to be the same over time and for different accounts.
            Can't be used to download or reuse the file.

        width (``int``):
            Video width as defined by sender.

        height (``int``):
            Video height as defined by sender.

        duration (``int``):
            Duration of the video in seconds as defined by sender.

        mime_type (``str``, *optional*):
            Mime type of a file as defined by sender.

        file_size (``int``, *optional*):
            File size.
    """
    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        duration: int,
        mime_type: Optional[str] = None,
        file_size: Optional[int] = None,
    ):
        super().__init__(client)

        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.width = width
        self.height = height
        self.duration = duration
        self.mime_type = mime_type
        self.file_size = file_size

    @staticmethod
    def _parse(
        client,
        video: "raw.types.Document",
        video_attributes: "raw.types.DocumentAttributeVideo",
    ) -> "LivePhoto":
        return LivePhoto(
            file_id=FileId(
                file_type=FileType.VIDEO,
                dc_id=video.dc_id,
                media_id=video.id,
                access_hash=video.access_hash,
                file_reference=video.file_reference
            ).encode(),
            file_unique_id=FileUniqueId(
                file_unique_type=FileUniqueType.DOCUMENT,
                media_id=video.id
            ).encode(),
            width=getattr(video_attributes, "w", None),
            height=getattr(video_attributes, "h", None),
            duration=video_attributes.duration,
            mime_type=video.mime_type,
            file_size=video.size,
            client=client
        )
