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


class PlaceGiftAuctionBid:
    async def place_gift_auction_bid(
        self: "pyrogram.Client",
        gift_id: int,
        star_count: int,
        user_id: Optional[Union[int, str]] = None,
        text: Optional["types.FormattedText"] = None,
        is_private: Optional[bool] = False,
    ) -> bool:
        """Places a bid on an auction gift.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            gift_id (``int``):
                Identifier of the gift to place the bid on.

            star_count (``int``):
                The number of Telegram Stars to place in the bid.

            user_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target chat you want to transfer the star gift to.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            text (:obj:`~pyrogram.types.FormattedText`, *optional*):
                Text to show along with the gift.
                Must be empty if the receiver enabled paid messages.

            is_private (``bool``, *optional*):
                Pass True to show gift text and sender only to the gift receiver, otherwise, everyone will be able to see them.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Place a bid of 100 stars on a gift auction for yourself
                await app.place_gift_auction_bid(
                    gift_id=12345,
                    star_count=100
                )

                # Place a bid of 250 stars on a gift auction for another user with a message
                await app.place_gift_auction_bid(
                    gift_id=12345,
                    star_count=250,
                    user_id="@KurimuzonAkuma",
                    text=types.FormattedText(
                        text="Here's a gift for you!"
                    )
                )
        """
        invoice = raw.types.InputInvoiceStarGiftAuctionBid(
            gift_id=gift_id,
            bid_amount=star_count,
            hide_name=is_private,
            update_bid=False,
            peer=await self.resolve_peer(user_id or "me"),
            message=await text.write() if text else None
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
