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


class GetGiftUpgradePreview:
    async def get_gift_upgrade_preview(
        self: "pyrogram.Client",
        gift_id: int
    ) -> "types.GiftUpgradePreview":
        """Return examples of possible upgraded gifts for a regular gift.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            gift_id (``int``):
                Identifier of the gift.

        Returns:
            :obj:`~pyrogram.types.GiftUpgradePreview`: Information about the gift preview is returned.

        Example:
            .. code-block:: python

                # Get information about upgraded gift preview
                await client.get_gift_upgrade_preview(5936085638515261992)
        """
        r = await self.invoke(
            raw.functions.payments.GetStarGiftUpgradePreview(
                gift_id=gift_id
            )
        )

        return await types.GiftUpgradePreview._parse(self, r)
