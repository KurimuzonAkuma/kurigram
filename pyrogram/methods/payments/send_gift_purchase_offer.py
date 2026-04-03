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
from pyrogram import raw, types, utils


class SendGiftPurchaseOffer:
    async def send_gift_purchase_offer(
        self: "pyrogram.Client",
        owner_id: Union[int, str],
        gift_name: str,
        price: "types.GiftResalePrice",
        duration: int,
        paid_message_star_count: Optional[int] = None
    ) -> "types.Message":
        """Sends an offer to purchase an upgraded gift.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            owner_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat that currently owns the gift and will receive the offer.
                For a contact that exists in your Telegram address book you can use his phone number (str).

            gift_name (``str``):
                Name or link of the upgraded gift.

            price (:obj:`~pyrogram.types.GiftResalePrice`):
                The price that the user agreed to pay for the gift.

            duration (``int``):
                Duration of the offer, in seconds.
                Must be one of 21600, 43200, 86400, 129600, 172800, or 259200.

            paid_message_star_count (``int``, *optional*):
                The number of Telegram Stars the user agreed to pay additionally for sending of the offer message to the current gift owner.
                Pass User.paid_message_star_count for users and None otherwise.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent Message is returned.
        """
        match = self.UPGRADED_GIFT_RE.match(gift_name)

        if match:
            gift_name = match.group(1)

        r = await self.invoke(
            raw.functions.payments.SendStarGiftOffer(
                peer=await self.resolve_peer(owner_id),
                slug=gift_name,
                price=price.write(),
                duration=duration,
                random_id=self.rnd_id(),
                allow_paid_stars=paid_message_star_count
            )
        )

        return next(iter(await utils.parse_messages(client=self, messages=r)), None)
