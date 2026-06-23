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

from typing import Callable, Optional, Union

import pyrogram
from pyrogram import raw

from .input_media import InputMedia


class InputMediaLink(InputMedia):
    """Represents an HTTP link to be sent.

    Parameters:
        url (``str``):
            HTTP URL of the link.
    """

    def __init__(
        self,
        url: str,
    ):
        super().__init__()

        self.url = url

    async def write(
        self,
        *,
        client: "pyrogram.Client",
        chat_id: Optional[Union[int, str]] = None,
        progress: Optional[Callable] = None,
        progress_args: tuple = (),
        **kwargs,
    ) -> "raw.base.InputMedia":
        return raw.types.InputMediaWebPage(url=self.url)
