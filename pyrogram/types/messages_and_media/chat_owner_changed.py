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


class ChatOwnerChanged(Object):
    """Describes a service message about an ownership change in the chat.

    Parameters:
        new_owner (:obj:`~pyrogram.types.User`):
            The new owner of the chat.
    """

    def __init__(self, *, new_owner: "types.User"):
        super().__init__()

        self.new_owner = new_owner

    @staticmethod
    def _parse(
        client: "pyrogram.Client",
        action: "raw.types.MessageActionChangeCreator",
        users: Dict[int, "types.User"],
    ) -> "ChatOwnerChanged":
        if isinstance(action, raw.types.MessageActionChangeCreator):
            return ChatOwnerChanged(
                new_owner=types.User._parse(client, users.get(action.new_creator_id))
            )
