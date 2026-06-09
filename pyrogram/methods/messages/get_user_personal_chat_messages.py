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

import logging
from typing import AsyncIterator, Union

import pyrogram
from pyrogram import raw, types, utils

log = logging.getLogger(__name__)


class GetUserPersonalChatMessages:
    async def get_user_personal_chat_messages(
        self: "pyrogram.Client",
        user_id: Union[int, str],
        limit: int = 0,
        min_id: int = 0,
        max_id: int = 0,
    ) -> AsyncIterator["types.Message"]:
        """Use this method to get the last messages from the personal chat (i.e., the chat currently added to their profile) of a given user.

        The messages are returned in reverse chronological order.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            limit (``int``, *optional*):
                Limits the number of messages to be retrieved.
                By default, no limit is applied and all messages are returned.

            min_id (``int``, *optional*):
                If a positive value was provided, the method will return only messages
                with IDs more than or equal to min_id (inclusive).

            max_id (``int``, *optional*):
                If a positive value was provided, the method will return only messages
                with IDs less than or equal to max_id (inclusive).

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.
        """
        current = 0
        total = limit or (1 << 31) - 1
        limit = min(20, total)

        min_id = (min_id - 1) if min_id else 0
        max_id = (max_id + 1) if max_id else 0

        history = await self.invoke(
            raw.functions.messages.GetPersonalChannelHistory(
                user_id=await self.resolve_peer(user_id),
                limit=limit,
                max_id=max_id,
                min_id=min_id,
                hash=0,
            ),
            sleep_threshold=60,
        )

        messages = await utils.parse_messages(self, history, replies=0)

        if not messages:
            return

        for message in messages:
            yield message

            current += 1

            if current >= total:
                return
