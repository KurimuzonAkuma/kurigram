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

import pyrogram
from pyrogram import raw


class IncreaseGiftAuctionBid:
    async def increase_gift_auction_bid(
        self: "pyrogram.Client",
        gift_id: int,
        star_count: int
    ) -> bool:
        """Increases a bid for an auction gift without changing gift text and receiver.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            gift_id (``int``):
                Identifier of the gift to put the bid on.

            star_count (``int``):
                The number of Telegram Stars to put in the bid.

        Returns:
            ``bool``: On success, True is returned.
        """
        invoice = raw.types.InputInvoiceStarGiftAuctionBid(
            gift_id=gift_id,
            bid_amount=star_count,
            update_bid=True
        )

        form = await self.invoke(
            raw.functions.payments.GetPaymentForm(
                invoice=invoice
            )
        )

        if star_count < 0:
            raise ValueError("Invalid amount of Telegram Stars specified.")

        if form.invoice.prices[0].amount > star_count:
            raise ValueError("Have not enough Telegram Stars.")

        r = await self.invoke(
            raw.functions.payments.SendStarsForm(
                form_id=form.form_id,
                invoice=invoice
            )
        )

        return isinstance(r, raw.types.payments.PaymentResult)
