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

import logging
import re
from typing import Union

import pyrogram
from pyrogram import raw, types

log = logging.getLogger(__name__)


class GetGiftAuctionState:
    async def get_gift_auction_state(
        self: "pyrogram.Client", auction_id: Union[str, int]
    ) -> "types.GiftAuctionState":
        """Returns auction state for a gift.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            auction_id (``str`` | ``int``):
                Unique identifier of the auction, auction link or gift id.

        Returns:
            :obj:`~pyrogram.types.GiftAuctionState`: On success, the auction state is returned.
        """
        if isinstance(auction_id, int):
            auction = raw.types.InputStarGiftAuction(gift_id=auction_id)
        else:
            match = re.match(r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/(?:auction/))([\w-]+)$", auction_id)

            if match:
                slug = match.group(1)
            elif isinstance(auction_id, str):
                slug = auction_id
            else:
                raise ValueError("Invalid auction link")

            auction=raw.types.InputStarGiftAuctionSlug(slug=slug)

        r = await self.invoke(
            raw.functions.payments.GetStarGiftAuctionState(
                auction=auction, version=0
            )
        )

        return await types.GiftAuctionState._parse(self, r)
