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

class DeclineSuggestedPost():
    async def decline_suggested_post(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        comment: Optional[str] = None
    ) -> bool:
        """Use this method to decline a suggested post in a direct messages chat.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of a suggested post message to decline.

            comment (``str``, *optional*):
                Comment for the creator of the suggested post, 0-128 characters.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.decline_suggested_post(chat_id, message_id, "I don't like this picture!")

        """
        await self.invoke(
            raw.functions.messages.ToggleSuggestedPostApproval(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
                reject=True,
                reject_comment=comment
            )
        )

        return True
