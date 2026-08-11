#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present <https://github.com/TelegramPlayGround>
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
from typing import Optional

from pyrogram import enums

from .message_origin import MessageOrigin


class MessageOriginImport(MessageOrigin):
    """Contains information about a message imported from a foreign chat service.

    Parameters:
        type (:obj:`~pyrogram.enums.MessageOriginType`):
            Type of the message origin.

        date (:py:obj:`~datetime.datetime`):
            Date the message was sent originally.

        sender_user_name (``str``):
            Name of the original sender.
    """
    def __init__(
        self,
        *,
        date: Optional[datetime] = None,
        sender_user_name: Optional[str] = None
    ):
        super().__init__(
            type=enums.MessageOriginType.IMPORT,
            date=date
        )

        self.sender_user_name = sender_user_name
