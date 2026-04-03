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
from pyrogram.errors import MessageIdsEmpty

from ..object import Object


class SuggestedPostApproved(Object):
    """Describes a service message about the approval of a suggested post.

    Parameters:
        suggested_post_message_id (``int``, *optional*):
            Identifier of the message with the suggested post.

        suggested_post_message (:obj:`~pyrogram.types.Message`, *optional*):
            Message containing the suggested post.

        price (:obj:`~pyrogram.types.SuggestedPostPrice`, *optional*):
            Amount paid for the post.

        send_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the post will be published.
    """
    def __init__(
        self, *,
        suggested_post_message_id: Optional[int] = None,
        suggested_post_message: Optional["types.Message"] = None,
        price: Optional["types.SuggestedPostPrice"] = None,
        send_date: Optional[datetime] = None
    ):
        super().__init__()

        self.suggested_post_message_id = suggested_post_message_id
        self.suggested_post_message = suggested_post_message
        self.price = price
        self.send_date = send_date

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        message: "raw.types.MessageService"
    ) -> "SuggestedPostApproved":
        action: "raw.types.MessageActionSuggestedPostApproval" = message.action

        if not isinstance(action, raw.types.MessageActionSuggestedPostApproval):
            return None

        from_id = utils.get_peer_id(message.from_id) if message.from_id else None
        peer_id = utils.get_peer_id(message.peer_id)
        chat_id = peer_id or from_id

        suggested_post_message_id = None
        suggested_post_message = None

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

        return SuggestedPostApproved(
            suggested_post_message_id=suggested_post_message_id,
            suggested_post_message=suggested_post_message,
            price=types.SuggestedPostPrice._parse(action.price),
            send_date=utils.timestamp_to_datetime(action.schedule_date)
        )
