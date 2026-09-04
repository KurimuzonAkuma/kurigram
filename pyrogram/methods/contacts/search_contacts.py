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
from pyrogram import types


class SearchContacts:
    async def search_contacts(
        self: "pyrogram.Client",
        query: str,
        limit: int = 0
    ) -> "types.FoundContacts":
        """Returns users or channels found by name substring and auxiliary data.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            query (``str``):
                Target substring.

            limit (``int``, *optional*):
                Maximum number of users to be returned.

        Returns:
            :obj:`~pyrogram.types.FoundContacts`: On success, a list of chats is returned.

        Example:
            .. code-block:: python

                await app.search_contacts("pyrogram")
        """
        total = limit or (1 << 31) - 1
        limit = min(100, total)

        r = await self.invoke(
            raw.functions.contacts.Search(
                q=query,
                limit=limit
            )
        )

        return await types.FoundContacts._parse(self, r)
