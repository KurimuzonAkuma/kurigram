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
from typing import AsyncGenerator, Union

import pyrogram
from pyrogram import raw, types, utils


async def get_chunk(
    *,
    client: "pyrogram.Client",
    chat_id: Union[int, str],
    topic_id: int,
    limit: int = 0,
    offset: int = 0,
    from_message_id: int = 0,
    from_date: datetime = utils.zero_datetime(),
    min_id: int = 0,
    max_id: int = 0,
    reverse: bool = False
):
    from_message_id = from_message_id or (1 if reverse else 0)

    messages = await client.invoke(
        raw.functions.messages.GetSavedHistory(
            peer=await client.resolve_peer(topic_id),
            offset_id=from_message_id,
            offset_date=utils.datetime_to_timestamp(from_date),
            add_offset=offset * (-1 if reverse else 1) - (limit if reverse else 0),
            limit=limit,
            max_id=max_id,
            min_id=min_id,
            hash=0,
            parent_peer=await client.resolve_peer(chat_id)
        ),
        sleep_threshold=60
    )

    messages = await utils.parse_messages(client, messages, replies=0)
    if reverse:
        messages.reverse()

    return messages

class GetDirectMessagesChatTopicHistory:
    async def get_direct_messages_chat_topic_history(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        topic_id: int,
        limit: int = 0,
        offset: int = 0,
        offset_id: int = 0,
        offset_date: datetime = utils.zero_datetime(),
        min_id: int = 0,
        max_id: int = 0,
        reverse: bool = False
    ) -> AsyncGenerator["types.Message", None]:
        """Return messages in the topic in a channel direct messages chat administered by the current user.

        The messages are returned in reverse chronological order.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            topic_id (``int``):
                Identifier of the topic which messages will be fetched.

            limit (``int``, *optional*):
                Limits the number of messages to be retrieved.
                By default, no limit is applied and all messages are returned.

            offset (``int``, *optional*):
                Sequential number of the first message to be returned.
                Negative values are also accepted and become useful in case you set offset_id or offset_date.

            offset_id (``int``, *optional*):
                Identifier of the first message to be returned.

            offset_date (:py:obj:`~datetime.datetime`, *optional*):
                Pass a date as offset to retrieve only older messages starting from that date.

            min_id (``int``, *optional*):
                If a positive value was provided, the method will return only messages with IDs more than min_id.

            max_id (``int``, *optional*):
                If a positive value was provided, the method will return only messages with IDs less than max_id.

            reverse (``bool``, *optional*):
                Pass True to retrieve the messages from oldest to newest.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.

        Example:
            .. code-block:: python

                async for message in app.get_direct_messages_chat_topic_history(chat_id, topic_id):
                    print(message.text)
        """
        current = 0
        total = limit or (1 << 31) - 1
        limit = min(100, total)

        while True:
            messages = await get_chunk(
                client=self,
                chat_id=chat_id,
                topic_id=topic_id,
                limit=limit,
                offset=offset,
                from_message_id=offset_id,
                from_date=offset_date,
                max_id=max_id,
                min_id=min_id,
                reverse=reverse
            )

            if not messages:
                return

            offset_id = messages[-1].id
            if reverse:
                offset_id += 1

            for message in messages:
                yield message

                current += 1

                if current >= total:
                    return
