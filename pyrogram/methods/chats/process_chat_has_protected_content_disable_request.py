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

from typing import Union

import pyrogram
from pyrogram import raw, types, utils


class ProcessChatHasProtectedContentDisableRequest:
    async def process_chat_has_protected_content_disable_request(
        self: "pyrogram.Client", chat_id: Union[int, str], request_message_id: int, approve: bool
    ) -> Union["types.Message", bool]:
        """Processes request to disable has_protected_content in a chat.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            request_message_id (``int``):
                Identifier of the message with the request.
                The message must be incoming and contain ``chat_protected_content_disable_requested`` param set.

            approve (``bool``):
                Pass True to approve the request, False to reject the request.

        Returns:
            :obj:`~pyrogram.types.Message` | ``bool``: On success, a service message will be returned (when applicable),
            otherwise, in case a message object couldn't be returned, True is returned.
        """

        r = await self.invoke(
            raw.functions.messages.ToggleNoForwards(
                peer=await self.resolve_peer(chat_id),
                enabled=approve,
                request_msg_id=request_message_id,
            )
        )

        return next(iter(await utils.parse_messages(client=self, messages=r)), True)
