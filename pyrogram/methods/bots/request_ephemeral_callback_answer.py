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


class RequestEphemeralCallbackAnswer:
    async def request_ephemeral_callback_answer(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        callback_data: Optional[Union[str, bytes]] = None,
        timeout: int = 10
    ):
        """Request a callback answer from bots, for a callback button attached to an ephemeral
        message. This is the equivalent of clicking an inline button containing callback data.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                The ephemeral message id the inline keyboard is attached on.

            callback_data (``str`` | ``bytes``, *optional*):
                Callback data associated with the inline button you want to get the answer from.

            timeout (``int``, *optional*):
                Timeout in seconds.

        Returns:
            The answer containing info useful for clients to display a notification at the top of
            the chat screen or as an alert.

        Raises:
            TimeoutError: In case the bot fails to answer within the given timeout.
            RPCError: In case of a Telegram RPC error.

        Example:
            .. code-block:: python

                await app.request_ephemeral_callback_answer(chat_id, message_id, "callback_data")
        """
        data = bytes(callback_data, "utf-8") if isinstance(callback_data, str) else callback_data

        return await self.invoke(
            raw.functions.ephemeral.GetCallbackAnswer(
                peer=await self.resolve_peer(chat_id),
                id=message_id,
                data=data
            ),
            retries=1,
            timeout=timeout
        )
