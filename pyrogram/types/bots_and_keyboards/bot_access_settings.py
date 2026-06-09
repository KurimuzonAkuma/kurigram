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

from typing import List, Optional

from pyrogram import raw, types

from ..object import Object


class BotAccessSettings(Object):
    """This object describes the access settings of a bot.

    Parameters:
        is_access_restricted (``bool``):
            True, if only selected users can access the bot. The bot's owner can always access it.

        added_users (List of :obj:`~pyrogram.types.User`, *optional*):
            The list of other users who have access to the bot if the access is restricted.
    """

    def __init__(
        self, is_access_restricted: bool, added_users: Optional[List["types.User"]] = None
    ):
        super().__init__()

        self.is_access_restricted = is_access_restricted
        self.added_users = added_users

    @staticmethod
    def _parse(client, bot_access_settings: "raw.base.bots.AccessSettings"):
        return BotAccessSettings(
            is_access_restricted=bot_access_settings.restricted,
            added_users=types.List(
                [types.User._parse(client, i) for i in bot_access_settings.add_users]
            )
            if bot_access_settings.add_users
            else None,
        )
