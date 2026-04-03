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

from typing import Iterable, List, Optional, Union, overload
import re
import pyrogram
from pyrogram import raw, types, utils


class GetMessages:
    # Invalid arguments (chat and string message_id provided)
    @overload
    async def get_messages(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_ids: str,
        reply: None = None,
        pinned: None = None,
        replies: int = 1,
    ) -> Optional["types.Message"]: ...
    # Invalid arguments (only message_ids with type int or Iterable of int provided)
    @overload
    async def get_messages(
        self: "pyrogram.Client",
        chat_id: None = None,
        message_ids: Union[int, Iterable[int]] = 0,
        reply: None = None,
        pinned: None = None,
        replies: int = 1,
    ) -> None: ...
    # Invalid arguments (only chat provided)
    @overload
    async def get_messages(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_ids: None = None,
        reply: None = None,
        pinned: None = None,
        replies: int = 1,
    ) -> None: ...
    # Invalid arguments (only pinned provided)
    @overload
    async def get_messages(
        self: "pyrogram.Client",
        chat_id: None = None,
        message_ids: None = None,
        reply: None = None,
        pinned: bool = True,
        replies: int = 1,
    ) -> None: ...
    # Invalid arguments (nothing provided)
    @overload
    async def get_messages(
        self: "pyrogram.Client",
        chat_id: None = None,
        message_ids: None = None,
        reply: None = None,
        pinned: None = None,
        replies: int = 1,
    ) -> None: ...
    # One message
    @overload
    async def get_messages(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_ids: Union[int, str],
        reply: Optional[bool] = None,
        pinned: Optional[bool] = None,
        replies: int = 1,
    ) -> Optional["types.Message"]: ...
    # One message with string
    @overload
    async def get_messages(
        self: "pyrogram.Client",
        chat_id: None = None,
        message_ids: str = "",
        reply: Optional[bool] = None,
        pinned: Optional[bool] = None,
        replies: int = 1,
    ) -> Optional["types.Message"]: ...
    # Many messages
    @overload
    async def get_messages(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_ids: Iterable[int],
        reply: Optional[bool] = None,
        pinned: Optional[bool] = None,
        replies: int = 1,
    ) -> List["types.Message"]: ...
    # Pinned message
    @overload
    async def get_messages(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_ids: None = None,
        reply: Optional[bool] = None,
        pinned: bool = False,
        replies: int = 1,
    ) -> Optional["types.Message"]: ...
    # Pinned message with provided message ids
    # - message ids will not affect result
    @overload
    async def get_messages(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_ids: Optional[Union[int, Iterable[int], str]] = None,
        reply: Optional[bool] = None,
        pinned: bool = False,
        replies: int = 1,
    ) -> Optional["types.Message"]: ...
    async def get_messages(
        self: "pyrogram.Client",
        chat_id: Optional[Union[int, str]] = None,
        message_ids: Optional[Union[int, Iterable[int], str]] = None,
        reply: Optional[bool] = None,
        pinned: Optional[bool] = None,
        replies: int = 1,
    ) -> Union[Optional["types.Message"], List["types.Message"]]:
        """Get one or more messages from a chat by using message identifiers or link.

        You can retrieve up to 200 messages at once.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            message_ids (``int`` | Iterable of ``int`` | ``str``, *optional*):
                Pass a single message identifier or an iterable of message ids (as integers) or link to get the content of the
                message themselves or previous message you replied to using this message.

            reply (``bool``, *optional*):
                If True, you will get the content of
                the previous message you replied to using this message.

            pinned (``bool``, *optional*):
                If True, you will get last pinned message.

            replies (``int``, *optional*):
                The number of subsequent replies to get for each message.
                Pass 0 for no reply at all or -1 for unlimited replies.
                Defaults to 1.

        Returns:
            :obj:`~pyrogram.types.Message` | List of :obj:`~pyrogram.types.Message`: In case *message_ids* was not
            a list, a single message is returned, otherwise a list of messages is returned.

        Example:
            .. code-block:: python

                # Get one message
                await app.get_messages(chat_id=chat_id, message_ids=12345)

                # Get more than one message (list of messages)
                await app.get_messages(chat_id=chat_id, message_ids=[12345, 12346])

                # Get message by ignoring any replied-to message
                await app.get_messages(chat_id=chat_id, message_ids=message_id, replies=0)

                # Get message with all chained replied-to messages
                await app.get_messages(chat_id=chat_id, message_ids=message_id, replies=-1)

                # Get the replied-to message of a message
                await app.get_messages(chat_id=chat_id, message_ids=message_id, reply=True)

                # Get pinned message
                await app.get_messages(chat_id=chat_id, pinned=True)

                # Get message from link
                await app.get_messages(message_ids="https://t.me/pyrogram/49")

        Raises:
            ValueError: In case of invalid arguments.
        """
        is_iterable = not isinstance(message_ids, (int, str)) if message_ids is not None else False
        ids = None if message_ids is None else list(message_ids) if is_iterable else [message_ids]
        _type = raw.types.InputMessageReplyTo if reply else raw.types.InputMessageID

        if isinstance(message_ids, str):
            match = re.match(r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/(?:c/)?)([\w]+)(?:/\d+)*/(\d+)/?$", message_ids.lower())

            if match:
                try:
                    chat_id = utils.get_channel_id(int(match.group(1)))
                except ValueError:
                    chat_id = match.group(1)

                ids = [_type(id=int(match.group(2)))]
            else:
                raise ValueError("Invalid message link.")
        else:
            if not chat_id:
                raise ValueError("Invalid chat_id.")

            if pinned:
                ids = [raw.types.InputMessagePinned()]
            else:
                if ids is None:
                    raise ValueError("Invalid message ids.")

                ids = [_type(id=i) for i in ids]

        peer = await self.resolve_peer(chat_id)

        if replies < 0:
            replies = (1 << 31) - 1

        if isinstance(peer, raw.types.InputPeerChannel):
            rpc = raw.functions.channels.GetMessages(channel=peer, id=ids)
        else:
            rpc = raw.functions.messages.GetMessages(id=ids)

        r = await self.invoke(rpc, sleep_threshold=-1)

        messages = await utils.parse_messages(self, r, replies=replies)

        return messages if is_iterable else messages[0] if messages else None
