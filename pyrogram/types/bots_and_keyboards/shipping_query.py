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
from pyrogram import types, raw
from ..object import Object
from ..update import Update


class ShippingQuery(Object, Update):
    """This object contains information about an incoming shipping query.

    Parameters:
        id (``str``):
            Unique query identifier.

        from_user (:obj:`~pyrogram.types.User`):
            User who sent the query.

        invoice_payload (``str``):
            Bot-defined invoice payload, 1-128 bytes. This will not be displayed to the user, use for your internal processes.

        shipping_address (:obj:`~pyrogram.types.ShippingAddress`):
            User specified shipping address. Only available to the bot that received the payment.
    """

    def __init__(
        self,
        *,
        client: Optional["pyrogram.Client"] = None,
        id: str,
        from_user: "types.User",
        invoice_payload: str,
        shipping_address: Optional["types.ShippingAddress"] = None
    ):
        super().__init__(client)

        self.id = id
        self.from_user = from_user
        self.invoice_payload = invoice_payload
        self.shipping_address = shipping_address

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        shipping_query: "raw.types.UpdateBotShippingQuery",
        users: dict
    ) -> "ShippingQuery":
        # Try to decode shipping query payload into string. If that fails, fallback to bytes instead of decoding by
        # ignoring/replacing errors, this way, button clicks will still work.
        try:
            payload = shipping_query.payload.decode()
        except (UnicodeDecodeError, AttributeError):
            payload = shipping_query.payload

        return ShippingQuery(
            id=str(shipping_query.query_id),
            from_user=types.User._parse(client, users[shipping_query.user_id]),
            invoice_payload=payload,
            shipping_address=types.ShippingAddress._parse(shipping_query.shipping_address),
            client=client
        )

    async def answer(
        self,
        ok: bool,
        shipping_options: Optional["types.ShippingOptions"] = None,
        error_message: Optional[str] = None
    ):
        """Bound method *answer* of :obj:`~pyrogram.types.ShippingQuery`.

        Use this method as a shortcut for:

        .. code-block:: python

            await client.answer_shipping_query(
                shipping_query.id,
                ok=True
            )

        Example:
            .. code-block:: python

                await shipping_query.answer(ok=True)

        Parameters:
            ok (``bool``):
                Pass True if delivery to the specified address is possible and False if there are any problems (for example, if delivery to the specified address is not possible).

            shipping_options (:obj:`~pyrogram.types.ShippingOptions`, *optional*):
                Required if ok is True. A JSON-serialized array of available shipping options.

            error_message (``str``, *optional*):
                Required if ok is False. Error message in human readable form that explains why it is impossible to complete the order (e.g. "Sorry, delivery to your desired address is unavailable'). Telegram will display this message to the user.

        Returns:
            ``bool``: True, on success.
        """
        return await self._client.answer_shipping_query(
            shipping_query_id=self.id,
            ok=ok,
            shipping_options=shipping_options,
            error_message=error_message
        )
