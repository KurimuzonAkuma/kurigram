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

from typing import Optional, Union

import pyrogram
from pyrogram import raw, types

from ..object import Object


class InputPollOption(Object):
    """This object contains information about one answer option in a poll to be sent.

    Parameters:
        text (``str`` | :obj:`~pyrogram.enums.FormattedText`, *optional*):
            Option text, 1-100 characters.

        media (:obj:`~pyrogram.types.InputMediaPhoto` | :obj:`~pyrogram.types.InputMediaVideo` | :obj:`~pyrogram.types.InputMediaSticker` | :obj:`~pyrogram.types.Location`, *optional*):
            Media associated with the option.
            Currently supports only photo, video, sticker or location.
    """

    def __init__(
        self,
        *,
        text: Union[str, "types.FormattedText"],
        media: Optional[
            Union[
                "types.InputMediaPhoto",
                "types.InputMediaVideo",
                "types.InputMediaSticker",
                "types.Location",
            ]
        ] = None,
    ):
        super().__init__()

        self.text = text
        self.media = media

    async def write(self, client: "pyrogram.Client") -> "raw.types.InputPollAnswer":
        if isinstance(self.text, str):
            self.text = types.FormattedText(text=self.text)

        if self.media is not None and not isinstance(
            self.media,
            (
                types.InputMediaPhoto,
                types.InputMediaVideo,
                types.InputMediaSticker,
                types.Location,
            ),
        ):
            raise ValueError(f"Unsupported media type: {type(self.media)}")

        return raw.types.InputPollAnswer(
            text=await self.text.write(client),
            media=await self.media.write(client=client) if self.media is not None else None,
        )
