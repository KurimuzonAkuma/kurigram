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


class GetAccountTTL:
    async def get_account_ttl(
        self: "pyrogram.Client",
    ) -> int:
        """Get days to live of account.

        .. include:: /_includes/usable-by/users.rst

        Returns:
            ``int``: Time to live in days of the current account.

        Example:
            .. code-block:: python

                # Get ttl in days
                await app.get_account_ttl()
        """
        r = await self.invoke(
            raw.functions.account.GetAccountTTL()
        )

        return r.days
