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

from typing import Union, List, AsyncIterator, Optional
from datetime import datetime

import pyrogram
from pyrogram import raw, types, utils, enums


# noinspection PyShadowingBuiltins
async def get_chunk(
    client,
    chat_id: Union[int, str],
    query: str = "",
    filter: "enums.MessagesFilter" = enums.MessagesFilter.EMPTY,
    offset: int = 0,
    offset_id: int = 0,
    min_date: datetime = utils.zero_datetime(),
    max_date: datetime = utils.zero_datetime(),
    limit: int = 100,
    min_id: int = 0,
    max_id: int = 0,
    from_user: Optional[Union[int, str]] = None,
    message_thread_id: Optional[int] = None
) -> List["types.Message"]:
    r = await client.invoke(
        raw.functions.messages.Search(
            peer=await client.resolve_peer(chat_id),
            q=query,
            filter=filter.value(),
            min_date=utils.datetime_to_timestamp(min_date),
            max_date= utils.datetime_to_timestamp(max_date),
            offset_id=offset_id,
            add_offset=offset,
            limit=limit,
            min_id=min_id,
            max_id=max_id,
            from_id=(
                await client.resolve_peer(from_user)
                if from_user
                else None
            ),
            top_msg_id=message_thread_id,
            hash=0
        ),
        sleep_threshold=60
    )

    return await utils.parse_messages(client, r, replies=0)


class SearchMessages:
    # noinspection PyShadowingBuiltins
    async def search_messages(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        query: Optional[str] = "",
        offset: Optional[int] = 0,
        offset_id: Optional[int] = 0,
        min_date: Optional[datetime] = utils.zero_datetime(),
        max_date: Optional[datetime] = utils.zero_datetime(),
        min_id: Optional[int] = 0,
        max_id: Optional[int] = 0,
        filter: Optional["enums.MessagesFilter"] = enums.MessagesFilter.EMPTY,
        limit: Optional[int] = 0,
        from_user: Optional[Union[int, str]] = None,
        message_thread_id: Optional[int] = None
    ) -> AsyncIterator["types.Message"]:
        """Search for text and media messages inside a specific chat.

        If you want to get the messages count only, see :meth:`~pyrogram.Client.search_messages_count`.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            query (``str``, *optional*):
                Text query string.
                Required for text-only messages, optional for media messages (see the ``filter`` argument).
                When passed while searching for media messages, the query will be applied to captions.
                Defaults to "" (empty string).

            offset (``int``, *optional*):
                Sequential number of the first message to be returned.
                Defaults to 0.

            offset_id (``int``, *optional*):
                Identifier of the first message to be returned.

            min_date (:py:obj:`~datetime.datetime`, *optional*):
                Pass a date as offset to retrieve only older messages starting from that date.

            max_date (:py:obj:`~datetime.datetime`, *optional*):
                Pass a date as offset to retrieve only newer messages starting from that date.

            min_id (``int``, *optional*):
                If a positive value was provided, the method will return only messages with IDs more than min_id.

            max_id (``int``, *optional*):
                If a positive value was provided, the method will return only messages with IDs less than max_id.

            filter (:obj:`~pyrogram.enums.MessagesFilter`, *optional*):
                Pass a filter in order to search for specific kind of messages only.
                Defaults to any message (no filter).

            limit (``int``, *optional*):
                Limits the number of messages to be retrieved.
                By default, no limit is applied and all messages are returned.

            from_user (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target user you want to search for messages from.

            message_thread_id (``int``, *optional*):
                Unique identifier for the target message thread (topic) of the forum.
                For supergroups only.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Message` objects.

        Example:
            .. code-block:: python

                from pyrogram import enums

                # Search for text messages in chat. Get the last 120 results
                async for message in app.search_messages(chat_id, query="hello", limit=120):
                    print(message.text)

                # Search for pinned messages in chat
                async for message in app.search_messages(chat_id, filter=enums.MessagesFilter.PINNED):
                    print(message.text)

                # Search for messages containing "hello" sent by yourself in chat
                async for message in app.search_messages(chat, "hello", from_user="me"):
                    print(message.text)
        """

        current = 0
        total = abs(limit) or (1 << 31) - 1
        limit = min(100, total)

        while True:
            messages = await get_chunk(
                client=self,
                chat_id=chat_id,
                query=query,
                filter=filter,
                offset=offset,
                offset_id=offset_id,
                min_date=min_date,
                max_date=max_date,
                min_id=min_id,
                max_id=max_id,
                limit=limit,
                from_user=from_user,
                message_thread_id=message_thread_id
            )

            if not messages:
                return

            offset += len(messages)

            for message in messages:
                yield message

                current += 1

                if current >= total:
                    return
