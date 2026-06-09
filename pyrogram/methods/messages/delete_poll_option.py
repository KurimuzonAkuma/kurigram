#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present <https://github.com/TelegramPlayGround>
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

from typing import Union

import pyrogram
from pyrogram import raw, types, utils


class DeletePollOption:
    async def delete_poll_option(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        option: Union[str, "types.InputPollOption"],
    ) -> Union["types.Message", bool]:
        """Deletes an option from a poll.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".

            message_id (``int``):
                Identifier of the message containing the poll.

            option (``str``):
                Unique identifier of the option.

        Returns:
            :obj:`~pyrogram.types.Message` | ``bool``: On success, an edited message or a service message will be returned (when applicable),
            otherwise, in case a message object couldn't be returned, True is returned.

        Example:
            .. code-block:: python

                await app.delete_poll_option(
                    chat_id,
                    message_id,
                    option="1"
                )

        """
        r = await self.invoke(
            raw.functions.messages.DeletePollAnswer(
                peer=await self.resolve_peer(chat_id),
                msg_id=message_id,
                option=option.encode()
            )
        )

        return next(iter(await utils.parse_messages(client=self, messages=r)), True)
