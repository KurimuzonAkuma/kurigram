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
from pyrogram.methods.contacts.get_blocked_message_senders import (
    GetBlockedMessageSenders,
)


class FakeClient(GetBlockedMessageSenders):
    """A client that answers `contacts.GetBlocked` once, then an empty page."""

    def __init__(self, blocked, users) -> None:
        self.blocked = blocked
        self.users = users
        self.invocations = 0

    async def invoke(
        self, query: raw.functions.contacts.GetBlocked
    ) -> raw.types.contacts.Blocked:
        self.invocations += 1

        if self.invocations > 1:
            return raw.types.contacts.Blocked(blocked=[], chats=[], users=[])

        return raw.types.contacts.Blocked(blocked=self.blocked, chats=[], users=self.users)


@pytest.mark.asyncio
async def test_a_peer_missing_from_users_and_chats_is_skipped() -> None:
    # Chat._parse_chat() resolves to None when the peer isn't in either lookup map:
    #  the method used to yield that None straight through an iterator typed and
    #  documented to yield only Chat instances.
    client = FakeClient(
        blocked=[
            raw.types.PeerBlocked(peer_id=raw.types.PeerUser(user_id=7), date=1000),
            raw.types.PeerBlocked(peer_id=raw.types.PeerUser(user_id=999), date=2000),
        ],
        users=[
            raw.types.User(id=7, first_name="User 7", usernames=[], restriction_reason=[]),
        ],
    )

    chats = [chat async for chat in client.get_blocked_message_senders()]

    assert [chat.id for chat in chats] == [7]


@pytest.mark.asyncio
async def test_no_blocked_senders_yields_nothing() -> None:
    chats = [chat async for chat in FakeClient(blocked=[], users=[]).get_blocked_message_senders()]

    assert chats == []
