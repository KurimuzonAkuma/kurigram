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


class GetGiftUpgradeVariants:
    async def get_gift_upgrade_variants(
        self: "pyrogram.Client",
        gift_id: int
    ) -> "types.GiftUpgradeVariants":
        """Returns all possible variants of upgraded gifts for a regular gift.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            gift_id (``int``):
                Identifier of the gift.

        Returns:
            :obj:`~pyrogram.types.GiftUpgradeVariants`: On success, returns all possible variants of upgraded gifts for the given regular gift.
        """
        r = await self.invoke(
            raw.functions.payments.GetStarGiftUpgradeAttributes(
                gift_id=gift_id
            )
        )

        return await types.GiftUpgradeVariants._parse(self, r)
