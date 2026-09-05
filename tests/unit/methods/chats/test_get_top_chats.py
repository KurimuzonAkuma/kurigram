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

from pyrogram import enums, raw
from pyrogram.methods.chats.get_top_chats import GetTopChats


class FakeClient(GetTopChats):
    """A client that answers `contacts.GetTopPeers` once, then an empty page."""

    def __init__(self) -> None:
        self.invocations = 0

    async def invoke(self, query: raw.functions.contacts.GetTopPeers, **kwargs):
        self.invocations += 1

        if self.invocations > 1:
            return raw.types.contacts.TopPeers(categories=[], chats=[], users=[])

        return raw.types.contacts.TopPeers(
            categories=[
                raw.types.TopPeerCategoryPeers(
                    category=raw.types.TopPeerCategoryGroups(),
                    count=3,
                    peers=[
                        raw.types.TopPeer(peer=raw.types.PeerUser(user_id=7), rating=1.0),
                        raw.types.TopPeer(peer=raw.types.PeerChat(chat_id=42), rating=0.5),
                        # Neither a known user nor a known chat: _parse_chat resolves to
                        #  None for it, and it must be skipped rather than crash or yield
                        #  None through an iterator typed to yield only `Chat`.
                        raw.types.TopPeer(peer=raw.types.PeerUser(user_id=999), rating=0.1),
                    ],
                )
            ],
            chats=[
                raw.types.Chat(
                    id=42,
                    title="Group 42",
                    photo=raw.types.ChatPhotoEmpty(),
                    participants_count=10,
                    date=0,
                    version=0,
                )
            ],
            users=[
                raw.types.User(id=7, first_name="User 7", usernames=[], restriction_reason=[]),
            ],
        )


@pytest.mark.asyncio
async def test_group_and_user_peers_are_both_resolved() -> None:
    # `chats` used to be assigned the `r.chats` lookup dict and then immediately
    #  reassigned to the result list, so `chats.get(peer_id)` crashed with
    #  AttributeError for any peer that wasn't a user (list has no `.get`).
    chats = [chat async for chat in FakeClient().get_top_chats(enums.TopChatCategory.GROUPS)]

    # Public chat ids negate the raw group id; the raw lookup itself stays keyed by 42.
    assert [chat.id for chat in chats] == [7, -42]


@pytest.mark.asyncio
async def test_no_peers_yields_nothing() -> None:
    client = FakeClient()
    client.invocations = 1  # skip straight to the empty page

    chats = [chat async for chat in client.get_top_chats(enums.TopChatCategory.GROUPS)]

    assert chats == []
