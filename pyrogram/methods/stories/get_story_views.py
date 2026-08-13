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

from typing import AsyncIterator, Optional, Union

import pyrogram
from pyrogram import raw, types


class GetStoryViews:
    async def get_story_views(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        story_id: int,
        offset: str = "",
        limit: int = 0,
        contacts_only: Optional[bool] = None,
        reactions_first: Optional[bool] = None,
        forwards_first: Optional[bool] = None,
        query: Optional[str] = None
    ) -> AsyncIterator["types.StoryView"]:
        """Obtain the list of users that have viewed a specific story we posted.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            story_id (``int``):
                Pass a story identifier to get the story views.

            offset (``str``, *optional*):
                Offset of the results to be returned.

            limit (``int``, *optional*):
                Maximum number of views to return.

            contacts_only (``bool``, *optional*):
                Only Get views made by your contacts, Defaults to False.

            reactions_first (``bool``, *optional*):
                If True, return reactions first, Defaults to False.

            forwards_first (``bool``, *optional*):
                If True, return forwards first, Defaults to False.

            query (``str``, *optional*):
                Search for specific users.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.StoryView` objects.

        Example:
            .. code-block:: python

                # Get views
                async for view in app.get_story_views(chat_id, story_id):
                    print(view)
        """
        peer = await self.resolve_peer(chat_id)

        current = 0
        total = abs(limit) or (1 << 31) - 1
        limit = min(100, total)

        while True:
            r = await self.invoke(
                raw.functions.stories.GetStoryViewsList(
                    peer=peer,
                    id=story_id,
                    offset=offset,
                    limit=limit,
                    just_contacts=contacts_only,
                    reactions_first=reactions_first,
                    forwards_first=forwards_first,
                    q=query
                )
            )

            users = {i.id: i for i in r.users}
            chats = {i.id: i for i in r.chats}

            views = [
                types.StoryView._parse(self, i, users)
                for i in r.views
            ]

            if not views:
                return

            for view in views:
                yield view

                current += 1

                if current >= total:
                    return

            offset = r.next_offset

            if not offset:
                return
