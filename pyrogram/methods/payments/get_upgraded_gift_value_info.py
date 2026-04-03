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
from pyrogram import raw, types


class GetUpgradedGiftValueInfo:
    async def get_upgraded_gift_value_info(
        self: "pyrogram.Client",
        link: str
    ) -> "types.UpgradedGiftValueInfo":
        """Returns information about value of an upgraded gift by its name.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            link (``str``):
                The gift link or slug itself.

        Returns:
            :obj:`~pyrogram.types.UpgradedGiftValueInfo`: Information about the gift value is returned.

        Example:
            .. code-block:: python

                # Get information about upgraded gift value by link
                gift = await client.get_upgraded_gift_value_info("https://t.me/nft/SignetRing-903")

                # Get information about upgraded gift value by slug
                gift = await client.get_upgraded_gift_value_info("SignetRing-903")
        """
        match = self.UPGRADED_GIFT_RE.match(link)

        if match:
            slug = match.group(1)
        elif isinstance(link, str):
            slug = link
        else:
            raise ValueError("Invalid gift link")

        r = await self.invoke(
            raw.functions.payments.GetUniqueStarGiftValueInfo(
                slug=slug.replace(" ", "")
            )
        )

        return types.UpgradedGiftValueInfo._parse(r)
