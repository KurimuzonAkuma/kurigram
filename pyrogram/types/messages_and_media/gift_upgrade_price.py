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

from pyrogram import raw, utils

from ..object import Object


class GiftUpgradePrice(Object):
    """Describes a price required to pay to upgrade a gift.

    Parameters:
        date (:py:obj:`~datetime.datetime`):
            Date when the price will be in effect.

        star_count (``int``):
            The amount of Telegram Stars required to pay to upgrade the gift.
    """

    def __init__(
        self,
        *,
        date: datetime,
        star_count: int
    ):
        super().__init__()

        self.date = date
        self.star_count = star_count

    @staticmethod
    def _parse(attr: "raw.base.StarGiftUpgradePrice") -> "GiftUpgradePrice":
        return GiftUpgradePrice(
            date=utils.timestamp_to_datetime(attr.date),
            star_count=attr.upgrade_stars
        )
