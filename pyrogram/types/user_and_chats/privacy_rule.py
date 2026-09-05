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

from pyrogram import enums, raw, types

from ..object import Object


class PrivacyRule(Object):
    """A privacy rule.

    Parameters:
        type (:obj:`~pyrogram.enums.PrivacyRuleType`):
            Privacy rule type.

        users (List of :obj:`~pyrogram.types.User`, *optional*):
            List of users.

        chats (List of :obj:`~pyrogram.types.Chat`, *optional*):
            List of chats.
    """

    def __init__(
        self, *,
        type: "enums.PrivacyRuleType",
        users: Optional[List["types.User"]] = None,
        chats: Optional[List["types.Chat"]] = None
    ):
        super().__init__(None)

        self.type = type
        self.users = users
        self.chats = chats

    @staticmethod
    async def _parse(client, rule: "raw.base.PrivacyRule", users: dict, chats: dict) -> "PrivacyRule":
        return PrivacyRule(
            type=enums.PrivacyRuleType(type(rule)),
            users=types.List([await types.User._parse(client, users.get(i)) for i in getattr(rule, "users", [])]) or None,
            chats=types.List([await types.Chat._parse_chat(client, chats.get(i)) for i in getattr(rule, "chats", [])]) or None
        )
