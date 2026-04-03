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
from pyrogram import raw, types, utils


class SetGiftResalePrice:
    async def set_gift_resale_price(
        self: "pyrogram.Client",
        owned_gift_id: str,
        price: "types.GiftResalePrice" = None,
    ) -> bool:
        """Change resale price of a unique gift owned by the current user.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            owned_gift_id (``str``):
                Unique identifier of the target gift.
                For a user gift, you can use the message ID (int) of the gift message.
                For a channel gift, you can use the packed format `chatID_savedID` (str).
                For a upgraded gift, you can use the gift link.

            price (:obj:`~pyrogram.types.GiftResalePrice`, *optional*):
                The new price for the unique gift.
                Pass None to disallow gift resale.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Change resale price of a unique gift
                await app.set_gift_resale_price(
                    owned_gift_id="123456",
                    price=types.GiftResalePriceStar(star_count=100)
                )

                # Change resale price of a unique gift to 10 TONs
                await app.set_gift_resale_price(
                    owned_gift_id="123456",
                    price=types.GiftResalePriceTon(toncoin_cent_count=10000000000) # You can use utils.to_nano(10) for same result
                )

                # Disallow resale of a unique gift
                await app.set_gift_resale_price(owned_gift_id="123456")
        """
        await self.invoke(
            raw.functions.payments.UpdateStarGiftPrice(
                stargift=await utils.get_input_stargift(self, owned_gift_id),
                resell_amount=raw.types.StarsAmount(amount=0, nanos=0) if price is None else price.write()
            )
        )

        return True
