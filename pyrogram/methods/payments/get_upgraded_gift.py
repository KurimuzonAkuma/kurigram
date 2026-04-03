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


class GetUpgradedGift:
    async def get_upgraded_gift(
        self: "pyrogram.Client",
        link: str
    ) -> "types.Gift":
        """Get information about upgraded gift.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            link (``str``):
                The gift code link or slug itself.

        Returns:
            :obj:`~pyrogram.types.Gift`: Information about the gift is returned.

        Example:
            .. code-block:: python

                # Get information about upgraded gift by link
                gift = await client.get_upgraded_gift("https://t.me/nft/SignetRing-903")

                # Get information about upgraded gift by slug
                gift = await client.get_upgraded_gift("SignetRing-903")
        """
        match = self.UPGRADED_GIFT_RE.match(link)

        if match:
            slug = match.group(1)
        elif isinstance(link, str):
            slug = link
        else:
            raise ValueError("Invalid gift link")

        r = await self.invoke(
            raw.functions.payments.GetUniqueStarGift(
                slug=slug.replace(" ", "")
            )
        )

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        return await types.Gift._parse(self, r.gift, users=users, chats=chats)
