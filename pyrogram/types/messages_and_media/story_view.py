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

from datetime import datetime
from typing import List, Optional

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object


class StoryView(Object):
    """A story view date and reaction information.

    Parameters:
        from_user (:obj:`~pyrogram.types.User`):
            The user that viewed the story.

        date (:py:obj:`~datetime.datetime`):
            Date the story was viewed.

        is_blocked (``bool``, *optional*):
            Whether we have completely blocked this user, including from viewing more of our stories.

        is_blocked_my_stories_from (``bool``, *optional*):
            Whether we have blocked this user from viewing more of our stories.

        reaction (:obj:`~pyrogram.types.Reaction`, *optional*):
            Reaction that the user left on the story.
    """

    def __init__(
        self,
        *,
        client: Optional["pyrogram.Client"] = None,
        from_user: "types.User",
        date: datetime,
        is_blocked: Optional[bool] = None,
        is_blocked_my_stories_from: Optional[bool] = None,
        reaction: Optional["types.Reaction"] = None
    ):
        super().__init__(client)

        self.from_user = from_user
        self.date = date
        self.is_blocked = is_blocked
        self.is_blocked_my_stories_from = is_blocked_my_stories_from
        self.reaction = reaction

    @staticmethod
    def _parse(client, view: "raw.types.StoryView", users: List["raw.types.User"]) -> "StoryView":
        return StoryView(
            from_user=types.User._parse(client, users[view.user_id]),
            date=utils.timestamp_to_datetime(view.date),
            is_blocked=getattr(view, "blocked", None),
            is_blocked_my_stories_from=getattr(view, "blocked_my_stories_from", None),
            reaction=types.Reaction._parse(client, getattr(view, "reaction", None)),
            client=client
        )
