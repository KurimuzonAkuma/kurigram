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
from pyrogram import enums, raw


class SendPaidReaction:
    async def send_paid_reaction(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        amount: int,
        privacy: Optional["enums.PaidReactionPrivacy"] = None,
        send_as: Optional[Union[int, str]] = None,
    ) -> bool:
        """Send a paid reaction to a message.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the message.

            amount (``int``):
                Amount of stars to send.

            privacy (:obj:`~pyrogram.enums.PaidReactionPrivacy`, *optional*):
                Reaction privacy type.

            send_as (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the send_as chat.
                Applicable when privacy is :obj:`~pyrogram.enums.PaidReactionPrivacy.CHAT`.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                # Send paid reaction with 1 star
                await app.send_paid_reaction(chat_id, message_id, amount=1)
        """
        if privacy:
            is_queryable = privacy in [enums.PaidReactionPrivacy.CHAT]

            privacy = privacy.value(peer=await self.resolve_peer(send_as)) if is_queryable else privacy.value()

        rpc = raw.functions.messages.SendPaidReaction(
            peer=await self.resolve_peer(chat_id),
            msg_id=message_id,
            count=amount,
            random_id=self.rnd_id(),
            private=privacy
        )

        await self.invoke(rpc)

        return True
