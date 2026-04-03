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
from pyrogram import raw, types, utils


class ProcessGiftPurchaseOffer:
    async def process_gift_purchase_offer(
        self: "pyrogram.Client",
        message_id: int,
        accept: bool
    ) -> "types.Message":
        """Handles a pending gift purchase offer.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            message_id (``int``):
                Identifier of the message with the gift purchase offer.

            accept (``bool``):
                Pass True to accept the request.
                Pass False to reject it.

        Returns:
            :obj:`~pyrogram.types.Message`: On success, the sent Message is returned.
        """
        r = await self.invoke(
            raw.functions.payments.ResolveStarGiftOffer(
                offer_msg_id=message_id,
                decline=not accept
            )
        )

        return next(iter(await utils.parse_messages(client=self, messages=r)), None)
