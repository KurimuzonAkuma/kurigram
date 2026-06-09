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


class ChatHasProtectedContentDisableRequested(Object):
    """Chat ``has_protected_content`` setting was requested to be disabled.

    Parameters:
        is_expired (``bool``):
            True, if the request has expired.
    """

    def __init__(self, *, is_expired: bool):

        super().__init__()

        self.is_expired = is_expired

    @staticmethod
    def _parse(
        action: "raw.types.MessageActionNoForwardsRequest",
    ) -> "ChatHasProtectedContentDisableRequested":
        return ChatHasProtectedContentDisableRequested(is_expired=bool(action.expired))
