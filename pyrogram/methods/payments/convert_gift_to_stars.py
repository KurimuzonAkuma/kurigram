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
from pyrogram import raw, utils


class ConvertGiftToStars:
    async def convert_gift_to_stars(
        self: "pyrogram.Client",
        owned_gift_id: str,
        business_connection_id: str = None
    ) -> bool:
        """Convert a given regular gift to Telegram Stars.

        .. note::

            Requires the `can_convert_gifts_to_stars` business bot right.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            owned_gift_id (``str``):
                Unique identifier of the regular gift that should be converted to Telegram Stars.

            business_connection_id (``str``, *optional*):
                Unique identifier of the business connection.
                For bots only.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Convert gift
                await app.convert_gift_to_stars(message_id=123)
        """
        r = await self.invoke(
            raw.functions.payments.ConvertStarGift(
                stargift=await utils.get_input_stargift(self, owned_gift_id)
            ),
            business_connection_id=business_connection_id
        )

        return r
