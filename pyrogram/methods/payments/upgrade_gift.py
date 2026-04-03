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

import pyrogram
from pyrogram import errors, raw, types, utils


class UpgradeGift:
    async def upgrade_gift(
        self: "pyrogram.Client",
        owned_gift_id: str,
        keep_original_details: Optional[bool] = None,
        star_count: int = None,
        business_connection_id: str = None
    ) -> Optional["types.Message"]:
        """Upgrade a given regular gift to a unique gift.

        .. note::

            Requires the `can_transfer_and_upgrade_gifts` business bot right.
            Additionally requires the `can_transfer_stars` business bot right if the upgrade is paid.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            owned_gift_id (``str``):
                Unique identifier of the regular gift that should be upgraded to a unique one.
                For a user gift, you can use the message ID (int) of the gift message.
                For a channel gift, you can use the packed format `chatID_savedID` (str).
                For a upgraded gift, you can use the gift link.

            keep_original_details (``bool``, *optional*):
                Pass True to keep the original gift text, sender and receiver in the upgraded gift.

            star_count (``int``, *optional*):
                The amount of Telegram Stars required to pay for the upgrade.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection.
                For bots only.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent message is returned.

        Example:
            .. code-block:: python

                # Upgrade gift
                await app.upgrade_gift(owned_gift_id="123")

                # Upgrade gift in channel (owned_gift_id packed in format chatID_savedID)
                await app.upgrade_gift(owned_gift_id="123_456")
        """
        stargift = await utils.get_input_stargift(self, owned_gift_id)

        try:
            r = await self.invoke(
                raw.functions.payments.UpgradeStarGift(
                    stargift=stargift,
                    keep_original_details=keep_original_details
                ),
                business_connection_id=business_connection_id
            )
        except errors.PaymentRequired:
            invoice = raw.types.InputInvoiceStarGiftUpgrade(
                stargift=stargift,
                keep_original_details=keep_original_details
            )

            form = await self.invoke(
                raw.functions.payments.GetPaymentForm(
                    invoice=invoice
                ),
                business_connection_id=business_connection_id
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
                ),
                business_connection_id=business_connection_id
            )

        messages = await utils.parse_messages(
            client=self,
            messages=r.updates if isinstance(r, raw.types.payments.PaymentResult) else r
        )

        return messages[0] if messages else None
