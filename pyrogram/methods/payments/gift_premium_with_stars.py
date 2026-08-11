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


from typing import List, Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils


class GiftPremiumWithStars:
    async def gift_premium_with_stars(
        self: "pyrogram.Client",
        user_id: Union[int, str],
        month_count: int,
        text: Optional[str] = None,
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: Optional[List["types.MessageEntity"]] = None,
        star_count: Optional[int] = None,
    ) -> Optional["types.Message"]:
        """Allows to buy a Telegram Premium subscription for another user with payment in Telegram Stars.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat you want to transfer the star gift to.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            month_count (``int``):
                Number of months the Telegram Premium subscription will be active for the user.

            star_count (``int``, *optional*):
                The number of Telegram Stars to pay for subscription.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.

        Example:
            .. code-block:: python

                await app.gift_premium_with_stars(user_id=123, month_count=3)
        """
        text, entities = (await utils.parse_text_entities(self, text, parse_mode, entities)).values()
        entities = entities or []

        invoice = raw.types.InputInvoicePremiumGiftStars(
            user_id=await self.resolve_peer(user_id),
            months=month_count,
            message=raw.types.TextWithEntities(
                text=text,
                entities=entities,
            ) if text else None
        )

        form = await self.invoke(
            raw.functions.payments.GetPaymentForm(
                invoice=invoice
            )
        )

        if star_count is not None:
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

        messages = await utils.parse_messages(
            client=self,
            messages=r.updates if isinstance(r, raw.types.payments.PaymentResult) else r
        )

        return messages[0] if messages else None
