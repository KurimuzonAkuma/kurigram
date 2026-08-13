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


from typing import List, Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils


class SendGift:
    async def send_gift(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        gift_id: int,
        text: Optional[str] = None,
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: Optional[List["types.MessageEntity"]] = None,
        is_private: Optional[bool] = None,
        pay_for_upgrade: Optional[bool] = None,
    ) -> Optional["types.Message"]:
        """Send a gift to another user or channel chat. May return an error with a message "STARGIFT_USAGE_LIMITED" if the gift was sold out.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            gift_id (``int``):
                Unique identifier of star gift.
                To get all available star gifts use :meth:`~pyrogram.Client.get_available_gifts`.

            text (``str``, *optional*):
                Text that will be shown along with the gift, 0-128 characters.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in message text, which can be specified instead of *parse_mode*.

            is_private (``bool``, *optional*):
                Pass True to show gift text and sender only to the gift receiver. Otherwise, everyone will be able to see them.

            pay_for_upgrade (``bool``, *optional*):
                Pass True to additionally pay for the gift upgrade and allow the receiver to upgrade it for free.

        Returns:
            :obj:`~pyrogram.types.Message` | ``None``: On success, the sent message is returned, otherwise,
            in case the server answered with no message, None is returned.

        Example:
            .. code-block:: python

                # Send gift
                await app.send_gift(chat_id=chat_id, gift_id=123)
        """
        text, entities = (await utils.parse_text_entities(self, text, parse_mode, entities)).values()

        invoice = raw.types.InputInvoiceStarGift(
            peer=await self.resolve_peer(chat_id),
            gift_id=gift_id,
            hide_name=is_private,
            include_upgrade=pay_for_upgrade,
            message=raw.types.TextWithEntities(text=text, entities=entities or []) if text else None
        )

        r = await self.invoke(
            raw.functions.payments.SendStarsForm(
                form_id=(await self.invoke(
                    raw.functions.payments.GetPaymentForm(
                        invoice=invoice
                    )
                )).form_id,
                invoice=invoice
            )
        )

        messages = await utils.parse_messages(self, r.updates)

        return messages[0] if messages else None
