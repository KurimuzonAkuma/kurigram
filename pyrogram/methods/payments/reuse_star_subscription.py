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


class ReuseStarSubscription:
    async def reuse_star_subscription(self: "pyrogram.Client", subscription_id: str) -> bool:
        """Reuses an active Telegram Star subscription to a channel chat and joins the chat again.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            subscription_id (``str``):
                Identifier of the subscription.

        Returns:
            ``bool``: On success, True is returned.
        """
        return await self.invoke(
            raw.functions.payments.FulfillStarsSubscription(
                peer=raw.types.InputPeerSelf(),
                subscription_id=subscription_id,
            )
        )
