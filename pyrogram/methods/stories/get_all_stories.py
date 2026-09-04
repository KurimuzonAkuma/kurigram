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

from typing import AsyncGenerator, Optional

import pyrogram
from pyrogram import raw
from pyrogram import types


class GetAllStories:
    async def get_all_stories(
        self: "pyrogram.Client",
        next: Optional[bool] = None,
        hidden: Optional[bool] = None,
        state: Optional[str] = None,
    ) -> AsyncGenerator["types.Story", None]:
        """Get all active or hidden stories that displayed on the action bar on the homescreen.

        .. include:: /_includes/usable-by/users.rst

        Parameters
            next (``bool``, *optional*):
                If next and state are both set, uses the passed state to paginate to the next results.
                If neither state nor next are set, fetches the initial page.
                If state is set and next is not set, check for changes in the active/hidden peerset.

            hidden (``bool``, *optional*):
                If set, fetches the hidden active story list, otherwise fetches the active story list.

            state (``str``, *optional*):
                If next and state are both set, uses the passed state to paginate to the next results.
                If neither state nor next are set, fetches the initial page.
                If state is set and next is not set, check for changes in the active/hidden peerset.

        Returns:
            ``Generator``: On success, a generator yielding :obj:`~pyrogram.types.Story` objects is returned.

        Example:
            .. code-block:: python

                # Get all active story
                async for story in app.get_all_stories():
                    print(story)
        """

        r = await self.invoke(
            raw.functions.stories.GetAllStories(
                next=next,
                hidden=hidden,
                state=state
            )
        )

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        for peer_story in r.peer_stories:
            for story in peer_story.stories:
                yield await types.Story._parse(
                    self,
                    story,
                    peer_story.peer,
                    users,
                    chats
                )
