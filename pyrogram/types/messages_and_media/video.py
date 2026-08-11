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
from pyrogram import raw, types, utils
from pyrogram.file_id import FileId, FileType, FileUniqueId, FileUniqueType

from ..object import Object


class Video(Object):
    """A video file.

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

        codec (``str``):
            Codec used for video file encoding, for example, "h264", "h265", or "av1".

        duration (``int``):
            Duration of the video in seconds as defined by sender.

        file_name (``str``, *optional*):
            Video file name.

        mime_type (``str``, *optional*):
            Mime type of a file as defined by sender.

        file_size (``int``, *optional*):
            File size.

        supports_streaming (``bool``, *optional*):
            True, if the video was uploaded with streaming support.

        ttl_seconds (``int``. *optional*):
            Time-to-live seconds, for secret photos.

        date (:py:obj:`~datetime.datetime`, *optional*):
            Date the video was sent.

        thumbs (List of :obj:`~pyrogram.types.Thumbnail`, *optional*):
            Video thumbnails.

        video_cover (:obj:`~pyrogram.types.Photo`, *optional*):
            Video cover.

        video_start_timestamp (``int``, *optional*):
            Video startpoint, in seconds.

        alternative_videos (List of :obj:`~pyrogram.types.Video`, *optional*):
            Alternative qualities of the video in MPEG4 format, encoded with H.264 codec.
    """
    def __init__(
        self,
        *,
        client: Optional["pyrogram.Client"] = None,
        file_id: str,
        file_unique_id: str,
        width: int,
        height: int,
        codec: str,
        duration: int,
        file_name: Optional[str] = None,
        mime_type: Optional[str] = None,
        file_size: Optional[int] = None,
        supports_streaming: Optional[bool] = None,
        ttl_seconds: Optional[int] = None,
        date: Optional[datetime] = None,
        thumbs: Optional[List["types.Thumbnail"]] = None,
        video_cover: Optional["types.Photo"] = None,
        video_start_timestamp: Optional[int] = None,
        alternative_videos: Optional[List["types.Video"]] = []
    ):
        super().__init__(client)

        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.width = width
        self.height = height
        self.codec = codec
        self.duration = duration
        self.file_name = file_name
        self.mime_type = mime_type
        self.file_size = file_size
        self.supports_streaming = supports_streaming
        self.ttl_seconds = ttl_seconds
        self.date = date
        self.thumbs = thumbs
        self.video_cover = video_cover
        self.video_start_timestamp = video_start_timestamp
        self.alternative_videos = alternative_videos

    @staticmethod
    def _parse(
        client,
        video: "raw.types.Document",
        video_attributes: "raw.types.DocumentAttributeVideo",
        file_name: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
        video_cover = None,
        video_start_timestamp: Optional[int] = None,
        alternative_videos: List["raw.types.Document"] = []
    ) -> "Video":
        _alt_videos = types.List()

        for alt_doc in alternative_videos:
            alt_attrs = {type(i): i for i in alt_doc.attributes}
            alt_file_name = getattr(
                alt_attrs.get(raw.types.DocumentAttributeFilename), "file_name", None
            )
            alt_video_attr = alt_attrs.get(raw.types.DocumentAttributeVideo)

            if alt_video_attr:
                _alt_videos.append(
                    types.Video._parse(client, alt_doc, alt_video_attr, alt_file_name)
                )

        return Video(
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
            codec=getattr(video_attributes, "video_codec", None),
            duration=video_attributes.duration,
            file_name=file_name or f"video_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4",
            mime_type=video.mime_type,
            supports_streaming=video_attributes.supports_streaming,
            file_size=video.size,
            date=utils.timestamp_to_datetime(video.date),
            ttl_seconds=ttl_seconds,
            thumbs=types.Thumbnail._parse(client, video),
            video_cover=types.Photo._parse(client, video_cover),
            video_start_timestamp=video_start_timestamp,
            alternative_videos=_alt_videos or None,
            client=client
        )
