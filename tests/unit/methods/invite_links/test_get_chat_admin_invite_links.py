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
from pyrogram.methods.invite_links.get_chat_admin_invite_links import (
    GetChatAdminInviteLinks,
)

_CHAT_ID = -1001234567890
_ADMIN_ID = 7


class FakeClient(GetChatAdminInviteLinks):
    """A client that answers `messages.GetExportedChatInvites` once, then an empty page."""

    def __init__(self, invites) -> None:
        self.invites = invites
        self.invocations = 0

    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerChannel(channel_id=abs(peer_id), access_hash=0)

    async def invoke(
        self, query: raw.functions.messages.GetExportedChatInvites
    ) -> raw.types.messages.ExportedChatInvites:
        self.invocations += 1

        if self.invocations > 1:
            return raw.types.messages.ExportedChatInvites(count=0, invites=[], users=[])

        return raw.types.messages.ExportedChatInvites(
            count=len(self.invites),
            invites=self.invites,
            users=[
                raw.types.User(
                    id=_ADMIN_ID, first_name="Admin", usernames=[], restriction_reason=[]
                )
            ],
        )


@pytest.mark.asyncio
async def test_only_exported_invites_are_yielded() -> None:
    # ChatInviteLink._parse() returns None for any ExportedChatInvite variant other than
    #  ChatInviteExported (e.g. ChatInvitePublicJoinRequests): the method used to yield
    #  that None straight through an iterator typed and documented to yield only
    #  ChatInviteLink instances.
    client = FakeClient(
        [
            raw.types.ChatInviteExported(
                link="https://t.me/+aaaa", admin_id=_ADMIN_ID, date=1000
            ),
            raw.types.ChatInvitePublicJoinRequests(),
            raw.types.ChatInviteExported(
                link="https://t.me/+bbbb", admin_id=_ADMIN_ID, date=2000
            ),
        ]
    )

    links = [
        link
        async for link in client.get_chat_admin_invite_links(_CHAT_ID, _ADMIN_ID)
    ]

    assert [link.invite_link for link in links] == [
        "https://t.me/+aaaa",
        "https://t.me/+bbbb",
    ]


@pytest.mark.asyncio
async def test_no_invites_yields_nothing() -> None:
    links = [
        link
        async for link in FakeClient([]).get_chat_admin_invite_links(_CHAT_ID, _ADMIN_ID)
    ]

    assert links == []
