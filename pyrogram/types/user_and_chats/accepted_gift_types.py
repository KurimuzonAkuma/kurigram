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

from datetime import datetime
from typing import Optional

import pyrogram
from pyrogram import raw, types, utils

from ..object import Object


class AcceptedGiftTypes(Object):
    """Accepts gift types.

    Parameters:
        unlimited_gifts (``bool``, *optional*):
            TTrue, if unlimited regular gifts are accepted.

        limited_gifts (``bool``, *optional*):
            True, if limited regular gifts are accepted.

        upgraded_gifts (``bool``, *optional*):
            True, if upgraded gifts and regular gifts that can be upgraded for free are accepted.

        gifts_from_channels (``bool``, *optional*):
            True, if gifts from channels are accepted subject to other restrictions.

        premium_subscription (``bool``, *optional*):
            True, if Telegram Premium subscription is accepted.
    """

    def __init__(
        self,
        *,
        unlimited_gifts: Optional[bool] = None,
        limited_gifts: Optional[bool] = None,
        upgraded_gifts: Optional[bool] = None,
        gifts_from_channels: Optional[bool] = None,
        premium_subscription: Optional[bool] = None,
    ):
        super().__init__()

        self.unlimited_gifts = unlimited_gifts
        self.limited_gifts = limited_gifts
        self.upgraded_gifts = upgraded_gifts
        self.gifts_from_channels = gifts_from_channels
        self.premium_subscription = premium_subscription

    @staticmethod
    def _parse(disallowed_gifts: "raw.types.DisallowedGiftsSettings") -> Optional["AcceptedGiftTypes"]:
        if not disallowed_gifts:
            return None

        return AcceptedGiftTypes(
            limited_gifts=not disallowed_gifts.disallow_limited_stargifts,
            unlimited_gifts=not disallowed_gifts.disallow_unlimited_stargifts,
            upgraded_gifts=not disallowed_gifts.disallow_unique_stargifts,
            gifts_from_channels=not disallowed_gifts.disallow_stargifts_from_channels,
            premium_subscription=not disallowed_gifts.disallow_premium_gifts,
        )

    def write(self) -> "raw.types.DisallowedGiftsSettings":
        return raw.types.DisallowedGiftsSettings(
            disallow_unlimited_stargifts=not self.unlimited_gifts,
            disallow_limited_stargifts=not self.limited_gifts,
            disallow_unique_stargifts=not self.upgraded_gifts,
            disallow_stargifts_from_channels=not self.gifts_from_channels,
            disallow_premium_gifts=not self.premium_subscription,
        )
