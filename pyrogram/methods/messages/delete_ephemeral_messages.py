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

from typing import Iterable, Union

import pyrogram
from pyrogram import raw, utils


class DeleteEphemeralMessages:
    async def delete_ephemeral_messages(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        receiver_id: Union[int, str],
        message_ids: Union[int, Iterable[int]],
    ) -> bool:
        """Delete one or more ephemeral messages.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            receiver_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the only user allowed to see this
                message.

            message_ids (``int`` | Iterable of ``int``):
                An iterable of message identifiers to delete (integers) or a single message id.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                # Delete one message
                await app.delete_ephemeral_messages(chat_id, receiver_id, message_id)

                # Delete multiple messages at once
                await app.delete_ephemeral_messages(chat_id, receiver_id, list_of_message_ids)
        """
        is_iterable = not isinstance(message_ids, int)
        message_ids = list(message_ids) if is_iterable else [message_ids]

        peer = await self.resolve_peer(chat_id)
        receiver = await utils.resolve_receiver(self, receiver_id)

        for message_id in message_ids:
            await self.invoke(
                raw.functions.ephemeral.DeleteMessage(
                    peer=peer,
                    receiver_id=receiver,
                    id=message_id,
                )
            )

        return True
