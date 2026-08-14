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


class SetAccountTTL:
    async def set_account_ttl(
        self: "pyrogram.Client",
        days: int
    ) -> bool:
        """Set days to live of account.

        .. note::

            Days should be in range 30-730

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            days (``int``):
                Time to live in days.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Set account ttl to 1 year
                await app.set_account_ttl(365)
        """
        r = await self.invoke(
            raw.functions.account.SetAccountTTL(
                ttl=raw.types.AccountDaysTTL(days=days)
            )
        )

        return r
