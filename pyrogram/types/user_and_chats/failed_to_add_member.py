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

from pyrogram import raw
from ..object import Object


class FailedToAddMember(Object):
    """Contains information about a user that has failed to be added to a chat.

    Parameters:
        user_id (``int``):
            User identifier.

        premium_would_allow_invite (``bool``, *optional*):
            True, if subscription to Telegram Premium would have allowed to add the user to the chat.

        premium_required_to_send_messages (``bool``, *optional*):
            True, if subscription to Telegram Premium is required to send the user chat invite link.
    """
    def __init__(
        self,
        *,
        user_id: int,
        premium_would_allow_invite: Optional[bool] = None,
        premium_required_to_send_messages: Optional[bool] = None,
    ):
        self.user_id = user_id
        self.premium_would_allow_invite = premium_would_allow_invite
        self.premium_required_to_send_messages = premium_required_to_send_messages

    @staticmethod
    def _parse(missing_invite: "raw.types.MissingInvitee") -> "FailedToAddMember":
        return FailedToAddMember(
            user_id=missing_invite.user_id,
            premium_would_allow_invite=missing_invite.premium_would_allow_invite,
            premium_required_to_send_messages=missing_invite.premium_required_for_pm
        )
