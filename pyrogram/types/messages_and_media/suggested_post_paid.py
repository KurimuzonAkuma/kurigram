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
from pyrogram import raw, types, utils
from pyrogram.errors import MessageIdsEmpty

from ..object import Object


class SuggestedPostPaid(Object):
    """Describes a service message about a successful payment for a suggested post.

    Parameters:
        suggested_post_message_id (``int``, *optional*):
            Identifier of the message with the suggested post.

        suggested_post_message (:obj:`~pyrogram.types.Message`, *optional*):
            Message containing the suggested post.

        amount (``int``, *optional*):
            The amount of the currency that was received by the channel in nanotoncoins.
            For payments in toncoins only.

        star_amount (:obj:`~pyrogram.types.StarAmount`, *optional*):
            The amount of Telegram Stars that was received by the channel.
            For payments in Telegram Stars only.
    """
    def __init__(
        self, *,
        suggested_post_message_id: int = None,
        suggested_post_message: Optional["types.Message"] = None,
        amount: int = None,
        star_amount: "types.StarAmount" = None,
    ):
        super().__init__()

        self.suggested_post_message_id = suggested_post_message_id
        self.suggested_post_message = suggested_post_message
        self.amount = amount
        self.star_amount = star_amount

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        message: "raw.types.MessageService"
    ) -> "SuggestedPostPaid":
        action: "raw.types.MessageActionSuggestedPostSuccess" = message.action

        if not isinstance(action, raw.types.MessageActionSuggestedPostSuccess):
            return None

        from_id = utils.get_peer_id(message.from_id) if message.from_id else None
        peer_id = utils.get_peer_id(message.peer_id)
        chat_id = peer_id or from_id

        suggested_post_message_id = None
        suggested_post_message = None
        amount = None
        star_amount = None

        if isinstance(message.reply_to, raw.types.MessageReplyHeader):
            suggested_post_message_id = message.reply_to.reply_to_msg_id

            if client.fetch_replies:
                try:
                    suggested_post_message = await client.get_messages(
                        chat_id=chat_id,
                        message_ids=suggested_post_message_id
                    )
                except MessageIdsEmpty:
                    pass

        if isinstance(action.price, raw.types.StarsTonAmount):
            amount = action.price.ton_amount
        elif isinstance(action.price, raw.types.StarsAmount):
            star_amount = types.StarAmount._parse(action.price)

        return SuggestedPostPaid(
            suggested_post_message_id=suggested_post_message_id,
            suggested_post_message=suggested_post_message,
            amount=amount,
            star_amount=star_amount
        )
