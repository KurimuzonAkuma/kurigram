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

from typing import Dict

import pyrogram
from pyrogram import raw, types

from ..object import Object


class ManagedBotUpdated(Object):
    """This object contains information about the creation or token update of a bot that is managed by the current bot.

    Parameters:
        user (:obj:`~pyrogram.types.User`):
            User that created the bot.

        bot (:obj:`~pyrogram.types.User`):
            Information about the bot.
            Token of the bot can be fetched using the method :meth:`~pyrogram.Client.get_managed_bot_token`.
    """

    def __init__(
        self,
        *,
        user: "types.User",
        bot: "types.User",
    ):
        super().__init__()

        self.user = user
        self.bot = bot

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        managed_bot_updated: "raw.types.UpdateManagedBot",
        users: Dict[int, "raw.types.User"],
    ) -> "ManagedBotUpdated":
        if not isinstance(managed_bot_updated, raw.types.UpdateManagedBot):
            return

        return ManagedBotUpdated(
            user=types.User._parse(client, users.get(managed_bot_updated.user_id)),
            bot=types.User._parse(client, users.get(managed_bot_updated.bot_id))
        )
