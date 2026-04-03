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


class AuctionBid(Object):
    """Describes a bid in an auction.

    Parameters:
        star_count (``int``):
            The number of Telegram Stars that were put in the bid.

        bid_date (``datetime``):
            Date when the bid was made.

        position (``int``):
            Position of the bid in the list of all bids.
    """

    def __init__(self, *, star_count: int, bid_date: datetime, position: int):
        super().__init__()

        self.star_count = star_count
        self.bid_date = bid_date
        self.position = position

    @staticmethod
    def _parse(auction_bid: "raw.base.AuctionBidLevel") -> "AuctionBid":
        return AuctionBid(
            star_count=auction_bid.amount,
            bid_date=utils.timestamp_to_datetime(auction_bid.date),
            position=auction_bid.pos,
        )
