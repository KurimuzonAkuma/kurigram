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
from pyrogram import raw


class SetUpgradedGiftColors:
    async def set_upgraded_gift_colors(
        self: "pyrogram.Client",
        upgraded_gift_colors_id: int
    ) -> bool:
        """Changes color scheme for the current user based on an owned or a hosted upgraded gift.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            upgraded_gift_colors_id (``int``):
                Identifier of the color scheme to use.

        Returns:
            ``bool``: On success, True is returned.
        """
        r = await self.invoke(
            raw.functions.account.UpdateColor(
                color=raw.types.InputPeerColorCollectible(
                    collectible_id=upgraded_gift_colors_id
                )
            )
        )

        return r
