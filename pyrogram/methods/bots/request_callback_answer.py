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

from typing import Union, Optional

import pyrogram
from pyrogram import raw, utils


class RequestCallbackAnswer:
    async def request_callback_answer(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        callback_data: Union[str, bytes],
        password: Optional[str] = None,
        timeout: int = 10
    ):
        """Request a callback answer from bots.
        This is the equivalent of clicking an inline button containing callback data.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_id (``int``):
                The message id the inline keyboard is attached on.

            callback_data (``str`` | ``bytes``):
                Callback data associated with the inline button you want to get the answer from.

            password (``str``, *optional*):
                When clicking certain buttons (such as BotFather's confirmation button to transfer ownership), if your account has 2FA enabled, you need to provide your account's password.
                The 2-step verification password for the current user. Only applicable, if the :obj:`~pyrogram.types.InlineKeyboardButton` contains ``callback_data_with_password``.

            timeout (``int``, *optional*):
                Timeout in seconds.

        Returns:
            The answer containing info useful for clients to display a notification at the top of the chat screen
            or as an alert.

        Raises:
            TimeoutError: In case the bot fails to answer within 10 seconds.
            ValueError: In case of invalid arguments.
            RPCError: In case of Telegram RPC error.

        Example:
            .. code-block:: python

                await app.request_callback_answer(chat_id, message_id, "callback_data")
        """

        # Telegram only wants bytes, but we are allowed to pass strings too.
        data = bytes(callback_data, "utf-8") if isinstance(callback_data, str) else callback_data

        if password:
            r = await self.invoke(
                raw.functions.account.GetPassword()
            )
            password = utils.compute_password_check(r, password)

        return await self.invoke(
            raw.functions.messages.GetBotCallbackAnswer(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
                data=data,
                password=password
            ),
            retries=1,
            timeout=timeout
        )
