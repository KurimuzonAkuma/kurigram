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


class SetInactiveSessionTTL:
    async def set_inactive_session_ttl(
        self: "pyrogram.Client",
        inactive_session_ttl_days: int
    ) -> bool:
        """Changes the period of inactivity after which sessions will automatically be terminated.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            inactive_session_ttl_days (``int``):
                New number of days of inactivity before sessions will be automatically terminated, 1-366 days.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Set inactive session ttl to 1 year
                await app.set_inactive_session_ttl(365)
        """
        r = await self.invoke(
            raw.functions.account.SetAuthorizationTTL(
                authorization_ttl_days=inactive_session_ttl_days
            )
        )

        return r
