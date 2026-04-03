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

from typing import Dict, List

import pyrogram
from pyrogram import raw

from ..object import Object


class ChatHasProtectedContentToggled(Object):
    """Chat ``has_protected_content`` setting was changed or request to change it was rejected.

    Parameters:
        request_message_id (``int``):
            True, if the request has expired.

        old_has_protected_content (``bool``):
            Previous value of the setting.

        new_has_protected_content (``bool``):
            New value of the setting.
    """

    def __init__(
        self,
        *,
        request_message_id: int,
        old_has_protected_content: bool,
        new_has_protected_content: bool,
    ):

        super().__init__()

        self.request_message_id = request_message_id
        self.old_has_protected_content = old_has_protected_content
        self.new_has_protected_content = new_has_protected_content

    @staticmethod
    def _parse(
        message_id: int,
        action: "raw.types.MessageActionNoForwardsToggle",
    ) -> "ChatHasProtectedContentToggled":
        return ChatHasProtectedContentToggled(
            request_message_id=message_id,
            old_has_protected_content=action.prev_value,
            new_has_protected_content=action.new_value,
        )
