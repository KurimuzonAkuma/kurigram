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

import pytest

from pyrogram import raw
from pyrogram.methods.chats.set_chat_direct_messages_group import (
    SetChatDirectMessagesGroup,
)


class FakeClient(SetChatDirectMessagesGroup):
    """A client that records the raw `broadcast_messages_allowed` it was sent."""

    def __init__(self) -> None:
        self.captured = "not-called"

    async def resolve_peer(self, chat_id):
        return raw.types.InputPeerChannel(channel_id=1, access_hash=0)

    async def invoke(self, query: raw.functions.channels.UpdatePaidMessagesPrice) -> bool:
        self.captured = query.broadcast_messages_allowed
        return True


@pytest.mark.asyncio
async def test_default_is_enabled_leaves_the_flag_unset() -> None:
    # `is_enabled: bool = Optional[None]` evaluated at runtime to the NoneType class
    #  itself (Optional[None] collapses to NoneType), not to None: every call that
    #  omitted is_enabled silently forwarded that class object as the raw flag value.
    client = FakeClient()

    await client.set_chat_direct_messages_group(1)

    assert client.captured is None


@pytest.mark.asyncio
async def test_explicit_is_enabled_is_forwarded() -> None:
    client = FakeClient()

    await client.set_chat_direct_messages_group(1, is_enabled=True)

    assert client.captured is True
