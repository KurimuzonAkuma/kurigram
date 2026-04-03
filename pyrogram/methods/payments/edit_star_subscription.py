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

import pyrogram
from pyrogram import raw


class EditStarSubscription:
    async def edit_star_subscription(
        self: "pyrogram.Client", subscription_id: str, is_canceled: bool
    ) -> bool:
        """Cancels or re-enables Telegram Star subscription.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            subscription_id (``str``):
                Identifier of the subscription to change.

            is_canceled (``bool``):
                New value of is_canceled.

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self.invoke(
            raw.functions.payments.ChangeStarsSubscription(
                peer=raw.types.InputPeerSelf(),
                subscription_id=subscription_id,
                canceled=is_canceled,
            )
        )
