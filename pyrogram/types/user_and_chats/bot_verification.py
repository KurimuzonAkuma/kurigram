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

from typing import Optional

from pyrogram import raw, types
from ..object import Object


class BotVerification(Object):
    """Information about bot verification.

    Parameters:
        bot (:obj:`~pyrogram.types.User`):
            Bot that is verified this user.

        custom_emoji_id (``str``):
            Custom emoji icon identifier.

        description (``int``, *optional*):
            Additional description about the verification.
    """

    def __init__(
        self,
        *,
        bot: int,
        custom_emoji_id: str,
        description: str
    ):
        self.bot = bot
        self.custom_emoji_id = custom_emoji_id
        self.description = description

    @staticmethod
    def _parse(
        client,
        verification: "raw.types.BotVerification",
        users
    ) -> Optional["BotVerification"]:
        if not verification:
            return None

        return BotVerification(
            bot=types.User._parse(client, users.get(verification.bot_id)),
            custom_emoji_id=str(verification.icon),
            description=verification.description
        )
