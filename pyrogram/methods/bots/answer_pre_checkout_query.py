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

import pyrogram
from pyrogram import raw


class AnswerPreCheckoutQuery:
    async def answer_pre_checkout_query(
        self: "pyrogram.Client",
        pre_checkout_query_id: str,
        ok: Optional[bool] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Send answers to pre-checkout queries.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            pre_checkout_query_id (``str``):
                Unique identifier for the query to be answered.

            ok (``bool``, *optional*):
                Set this flag if everything is alright (goods are available, etc.) and the bot is ready to proceed with the order.
                Otherwise do not set it, and set the error field, instead.

            error_message (``str``, *optional*):
                Error message in human readable form that explains the reason for failure to proceed with the checkout.
                Required if ``success`` isn't set.

        Returns:
            ``bool``: True, on success.

        Example:
            .. code-block:: python

                # Proceed with the order
                await app.answer_pre_checkout_query(query_id, ok=True)

                # Answer with error message
                await app.answer_pre_checkout_query(query_id, ok=False, error_message="Out of stock")
        """
        return await self.invoke(
            raw.functions.messages.SetBotPrecheckoutResults(
                query_id=int(pre_checkout_query_id),
                success=ok,
                error=error_message
            )
        )
