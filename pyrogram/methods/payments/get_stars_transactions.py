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

import pyrogram
from pyrogram import raw


class GetStarsTransactions:
    async def get_stars_transactions(
        self: "pyrogram.Client",
        chat_id: Optional[Union[int, str]] = None,
        offset: str = "",
        limit: int = 100,
        inbound: Optional[bool] = None,
        outbound: Optional[bool] = None,
        ascending: Optional[bool] = None,
        ton: Optional[bool] = None,
        subscription_id: Optional[str] = None,
    ) -> "raw.base.payments.StarsStatus":
        """Get Telegram Stars transactions of the current account or a target chat.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use ``"me"`` or ``"self"``.

            offset (``str``, *optional*):
                Offset for pagination. Defaults to ``""``.

            limit (``int``, *optional*):
                Number of transactions to fetch. Defaults to ``100``.

            inbound (``bool``, *optional*):
                Pass True to fetch only incoming transactions.

            outbound (``bool``, *optional*):
                Pass True to fetch only outgoing transactions.

            ascending (``bool``, *optional*):
                Pass True to fetch transactions in ascending order.

            ton (``bool``, *optional*):
                Pass True to fetch TON transactions instead of Stars transactions.

            subscription_id (``str``, *optional*):
                Fetch transactions for a specific subscription.

        Returns:
            :obj:`~pyrogram.raw.base.payments.StarsStatus`: On success, the stars status with transaction history is returned.

        Example:
            .. code-block:: python

                transactions = await app.get_stars_transactions(limit=2, inbound=True)
                for transaction in transactions.history:
                    print(transaction.id, transaction.date)

                bot_transactions = await app.get_stars_transactions(chat_id="pyrogrambot", limit=10)
        """
        if chat_id is None:
            peer = raw.types.InputPeerSelf()
        else:
            peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.payments.GetStarsTransactions(
                peer=peer,
                offset=offset,
                limit=limit,
                inbound=inbound,
                outbound=outbound,
                ascending=ascending,
                ton=ton,
                subscription_id=subscription_id
            )
        )
