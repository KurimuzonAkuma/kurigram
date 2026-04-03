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
from typing import Optional

from pyrogram import raw, utils

from ..object import Object


class GiftAuction(Object):
    """Describes an auction on which a gift can be purchased.

    Parameters:
        id (``str``):
            Identifier of the auction.

        gifts_per_round (``int``):
            Number of gifts distributed in each round.

        start_date (:py:obj:`~datetime.datetime`):
            Date when the auction will start.
    """

    def __init__(self, *, id: str, gifts_per_round: int, start_date: datetime):
        super().__init__()

        self.id = id
        self.gifts_per_round = gifts_per_round
        self.start_date = start_date

    @staticmethod
    def _parse(gift: "raw.types.StarGift") -> Optional["GiftAuction"]:
        if gift.auction_slug:
            return GiftAuction(
                id=gift.auction_slug,
                gifts_per_round=gift.gifts_per_round,
                start_date=utils.timestamp_to_datetime(gift.auction_start_date),
            )
