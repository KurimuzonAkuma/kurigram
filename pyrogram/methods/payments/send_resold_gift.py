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


class SendResoldGift:
    async def send_resold_gift(
        self: "pyrogram.Client",
        gift_link: str,
        new_owner_chat_id: Union[int, str],
        price: "types.GiftResalePrice",
    ) -> Optional["types.Message"]:
        """Send an upgraded gift that is available for resale to another user or channel chat.

        .. note::

            Gifts already owned by the current user must be transferred using :meth:`~pyrogram.Client.transfer_gift` and can't be passed to this method.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            gift_link (``str``):
                Link to the gift.

            new_owner_chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat you want to transfer the star gift to.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            price (:obj:`~pyrogram.types.GiftResalePrice`):
                The price that the user agreed to pay for the gift.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.

        Example:
            .. code-block:: python

                # Buy gift from telegram market and transfer it to another user
                await app.send_resold_gift(
                    gift_link="https://t.me/nft/NekoHelmet-9215",
                    new_owner_chat_id=123,
                    price=types.GiftResalePriceStar(star_count=100_000)
                )

                # Buy ton gift
                from pyrogram import utils

                await app.send_resold_gift(
                    gift_link="https://t.me/nft/NekoHelmet-9215",
                    new_owner_chat_id=123,
                    price=types.GiftResalePriceTon(
                        toncoin_cent_count=utils.to_nano(5) # 5 ton
                    )
                )
        """
        match = self.UPGRADED_GIFT_RE.match(gift_link)

        if not match:
            raise ValueError(
                "Invalid gift link provided."
            )

        peer = await self.resolve_peer(new_owner_chat_id)

        invoice = raw.types.InputInvoiceStarGiftResale(
            slug=match.group(1),
            to_id=peer,
            ton=isinstance(price, types.GiftResalePriceTon)
        )

        form = await self.invoke(
            raw.functions.payments.GetPaymentForm(
                invoice=invoice
            )
        )

        if isinstance(price, types.GiftResalePriceTon):
            amount = price.toncoin_cent_count
        else:
            amount = price.star_count

        if amount < 0:
            raise ValueError("Invalid price specified.")

        if form.invoice.prices[0].amount > amount:
            raise ValueError("Have not enough {}".format(
                "Toncoins" if isinstance(price, types.GiftResalePriceTon) else "Telegram Stars"
            ))

        r = await self.invoke(
            raw.functions.payments.SendStarsForm(
                form_id=form.form_id,
                invoice=invoice
            )
        )

        messages = await utils.parse_messages(
            client=self,
            messages=r.updates if isinstance(r, raw.types.payments.PaymentResult) else r
        )

        return messages[0] if messages else None
