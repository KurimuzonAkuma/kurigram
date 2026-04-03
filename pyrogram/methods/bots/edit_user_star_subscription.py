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

from typing import Union

import pyrogram
from pyrogram import raw


class EditUserStarSubscription:
    async def edit_user_star_subscription(
        self: "pyrogram.Client",
        user_id: Union[int, str],
        telegram_payment_charge_id: str,
        is_canceled: bool,
    ) -> bool:
        """Cancels or re-enables Telegram Star subscription for a user.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target user.

            telegram_payment_charge_id (``str``):
                Telegram payment identifier of the subscription.

            is_canceled (``bool``):
                Pass True to cancel the subscription.
                Pass False to allow the user to enable it.

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self.invoke(
            raw.functions.payments.BotCancelStarsSubscription(
                user_id=await self.resolve_peer(user_id),
                charge_id=telegram_payment_charge_id,
                restore=is_canceled,
            )
        )
