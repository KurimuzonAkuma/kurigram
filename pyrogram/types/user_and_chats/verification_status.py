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

from typing import Optional, Union

from pyrogram import raw

from ..object import Object


class VerificationStatus(Object):
    """Contains information about verification status of a chat or a user.

    Parameters:
        is_verified (``bool``, *optional*):
            True, if this user has been verified by Telegram.

        is_scam (``bool``, *optional*):
            True, if this user has been flagged for scam.

        is_fake (``bool``, *optional*):
            True, if this user has been flagged for impersonation.

        bot_verification_icon_custom_emoji_id (``str``, *optional*):
            Contains information about verification status of a user.
    """

    def __init__(
        self,
        *,
        is_verified: Optional[bool] = None,
        is_scam: Optional[bool] = None,
        is_fake: Optional[bool] = None,
        bot_verification_icon_custom_emoji_id: Optional[str] = None,
    ):
        super().__init__()

        self.is_verified = is_verified
        self.is_scam = is_scam
        self.is_fake = is_fake
        self.bot_verification_icon_custom_emoji_id = bot_verification_icon_custom_emoji_id

    @staticmethod
    def _parse(chat: Union["raw.base.User", "raw.base.Chat", "raw.base.ChatInvite"]) -> Optional["VerificationStatus"]:
        if not isinstance(chat, (raw.types.User, raw.types.Channel, raw.types.ChatInvite)):
            return None

        bot_verification_icon = None

        if isinstance(chat, raw.types.ChatInvite):
            bot_verification_icon = getattr(chat.bot_verification, "icon", None)
        else:
            bot_verification_icon = chat.bot_verification_icon

        return VerificationStatus(
            is_verified=chat.verified,
            is_scam=chat.scam,
            is_fake=chat.fake,
            bot_verification_icon_custom_emoji_id=str(bot_verification_icon) if bot_verification_icon else None
        )
