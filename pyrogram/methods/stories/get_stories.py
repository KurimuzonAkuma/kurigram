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

import re
from typing import Iterable, List, Optional, Union, overload

import pyrogram
from pyrogram import raw, types


class GetStories:
    @overload
    async def get_stories(
        self: "pyrogram.Client",
        chat_id: Optional[Union[int, str]] = None,
        story_ids: Optional[Union[int, str]] = None,
    ) -> Optional["types.Story"]: ...

    @overload
    async def get_stories(
        self: "pyrogram.Client",
        chat_id: Optional[Union[int, str]],
        story_ids: Iterable[int],
    ) -> List["types.Story"]: ...

    async def get_stories(
        self: "pyrogram.Client",
        chat_id: Optional[Union[int, str]] = None,
        story_ids: Optional[Union[int, Iterable[int], str]] = None,
    ) -> Optional[Union["types.Story", List["types.Story"]]]:
        """Get one or more stories from a chat by using stories identifiers.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target user.
                For your personal story you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            story_ids (``int`` | Iterable of ``int`` | ``str``, *optional*):
                Pass a single story identifier or an iterable of story ids (as integers)
                or link to get the content of the story themselves.

        Returns:
            :obj:`~pyrogram.types.Story` | List of :obj:`~pyrogram.types.Story` | ``None``: In case *story_ids* was not
            a list, a single story is returned, otherwise a list of stories is returned. In case *story_ids* was not a
            list and the story does not exist, None is returned.

        Example:
            .. code-block:: python

                # Get stories by id
                stories = await app.get_stories(chat_id, [1, 2, 3])

                for story in stories:
                    print(story)

        Raises:
            ValueError: In case of invalid arguments.
        """
        is_iterable = not isinstance(story_ids, (int, str)) if story_ids is not None else False
        ids = None if story_ids is None else list(story_ids) if is_iterable else [story_ids]

        if isinstance(story_ids, str):
            match = re.match(r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/)([\w]+)/s/(\d+)/?$", story_ids.lower())

            if match:
                chat_id = match.group(1)
                ids = [int(match.group(2))]
            else:
                raise ValueError("Invalid story link")
        else:
            if not chat_id:
                raise ValueError("Invalid chat_id.")

            if ids is None:
                raise ValueError("Invalid story_ids.")

        peer = await self.resolve_peer(chat_id)
        r = await self.invoke(
            raw.functions.stories.GetStoriesByID(
                peer=peer,
                id=ids
            )
        )

        stories = types.List()

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        for story in r.stories:
            stories.append(
                await types.Story._parse(
                    self,
                    story,
                    peer,
                    users,
                    chats
                )
            )

        return stories if is_iterable else stories[0] if stories else None
