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
from typing import Optional, Union
import pyrogram
from pyrogram import raw
from pyrogram import utils

class ApproveSuggestedPost():
    async def approve_suggested_post(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        send_date: Optional[datetime] = None
    ) -> bool:
        """Use this method to approve a suggested post in a direct messages chat.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of a suggested post message to approve.

            send_date (:py:obj:`~datetime.datetime`, *optional*):
                Date when the post is expected to be published.
                Omit if the date has already been specified when the suggested post was created.
                If specified, then the date must be not more than 2678400 seconds (30 days) in the future.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.approve_suggested_post(chat_id, message_id, send_date)

        """
        await self.invoke(
            raw.functions.messages.ToggleSuggestedPostApproval(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
                reject=False,
                schedule_date=utils.datetime_to_timestamp(send_date)
            )
        )

        return True
