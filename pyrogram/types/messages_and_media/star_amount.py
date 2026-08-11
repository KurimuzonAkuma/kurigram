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

from typing import Optional

from pyrogram import raw

from ..object import Object


class StarAmount(Object):
    """Describes a possibly non-integer amount of Telegram Stars.

    Parameters:
        star_count (``int``, *optional*):
            The integer amount of Telegram Stars rounded to 0.

        nanostar_count (``int``, *optional*):
            The number of 1/1000000000 shares of Telegram Stars.
            From -999999999 to 999999999.
    """

    def __init__(
        self, *,
        star_count: Optional[int] = None,
        nanostar_count: Optional[int] = None
    ):
        super().__init__()

        self.star_count = star_count
        self.nanostar_count = nanostar_count

    @staticmethod
    def _parse(action: "raw.types.StarsAmount") -> "StarAmount":
        if not isinstance(action, raw.types.StarsAmount):
            return None

        return StarAmount(
            star_count=action.amount,
            nanostar_count=action.nanos
        )
