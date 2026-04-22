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

from typing import Annotated, BinaryIO, Union

import pyrogram
from pyrogram import raw, types, media_utils

from ..object import Object


class InputPollOption(Object):
    """This object contains information about one answer option in a poll to be sent.

    Parameters:
        text (``str`` | :obj:`~pyrogram.enums.FormattedText`, *optional*):
            Option text, 1-100 characters.
        media (``str`` | :obj:`pyrogram.types.InputMediaPhoto|pyrogram.types.InputMediaVideo|pyrogram.types.Location|str`, *optional*):
            Media associated with the option. (photo, video, location, sticker)
    """

    def __init__(
        self,
        *,
        text: Union[str, "types.FormattedText"],
        media: Union[
            "types.InputMediaPhoto",
            "types.InputMediaVideo",
            Annotated[str, "sticker file_id"],
            "types.Location",
            None,
        ] = None,
    ):
        super().__init__()

        self.text = text
        self.media = media

    async def write(self, client: "pyrogram.Client") -> "raw.types.InputPollAnswer":
        if isinstance(self.text, str):
            self.text = types.FormattedText(text=self.text)

        if not self.media:
            raw_media = None
        elif isinstance(self.media, types.InputMediaPhoto):
            raw_media = await media_utils.resolve_to_raw_photo(client, self.media, chat_id="me")
        elif isinstance(self.media, types.InputMediaVideo):
            raw_media = await media_utils.resolve_to_raw_video(client, self.media, chat_id="me")
        elif isinstance(self.media, Union[BinaryIO, str]):
            raw_media = await media_utils.resolve_to_raw_sticker(client, self.media)
        elif isinstance(self.media, types.Location):
            raw_media = await media_utils.resolve_to_raw_location(self.media)
        else:
            raise ValueError("Unsupported media type: " + str(type(self.media)))

        return raw.types.InputPollAnswer(
            text=await self.text.write(client),
            media=raw_media,
        )
