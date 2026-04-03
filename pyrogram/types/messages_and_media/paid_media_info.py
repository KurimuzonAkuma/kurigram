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

from typing import List, Union

import pyrogram
from pyrogram import raw, types
from ..object import Object


class PaidMediaInfo(Object):
    """Describes the paid media added to a message.

    Parameters:
        stars_amount (``int``):
            The number of Telegram Stars that must be paid to buy access to the media.

        media (List of :obj:`~pyrogram.types.Photo` | :obj:`~pyrogram.types.Video` | :obj:`~pyrogram.types.PaidMediaPreview`):
            Information about the paid media.
    """

    def __init__(
        self,
        *,
        stars_amount: int,
        media: List[Union["types.Photo", "types.Video", "types.PaidMediaPreview"]]
    ):
        super().__init__()

        self.stars_amount = stars_amount
        self.media = media

    @staticmethod
    def _parse(
        client: "pyrogram.Client",
        message_paid_media: "raw.types.MessageMediaPaidMedia"
    ) -> "PaidMediaInfo":
        medias = []

        for extended_media in message_paid_media.extended_media:
            if isinstance(extended_media, raw.types.MessageExtendedMediaPreview):
                thumbnail = None

                if isinstance(getattr(extended_media, "thumb", None), raw.types.PhotoStrippedSize):
                    thumbnail = types.StrippedThumbnail._parse(client, extended_media.thumb)

                medias.append(
                    types.PaidMediaPreview(
                        width=getattr(extended_media, "w", None),
                        height=getattr(extended_media, "h", None),
                        duration=getattr(extended_media, "video_duration", None),
                        thumbnail=thumbnail,
                    )
                )
            elif isinstance(extended_media, raw.types.MessageExtendedMedia):
                media = extended_media.media

                if isinstance(media, raw.types.MessageMediaPhoto):
                    medias.append(types.Photo._parse(client, media.photo, media.ttl_seconds))
                elif isinstance(media, raw.types.MessageMediaDocument):
                    doc = media.document

                    attributes = {type(i): i for i in doc.attributes}

                    file_name = getattr(
                        attributes.get(
                            raw.types.DocumentAttributeFilename, None
                        ), "file_name", None
                    )

                    video_attributes = attributes[raw.types.DocumentAttributeVideo]

                    medias.append(types.Video._parse(client, doc, video_attributes, file_name, media.ttl_seconds))

        return PaidMediaInfo(
            stars_amount=message_paid_media.stars_amount,
            media=types.List(medias)
        )
