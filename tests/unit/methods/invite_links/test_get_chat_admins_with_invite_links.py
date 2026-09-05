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

from typing import Final, List

import pytest

from pyrogram import raw, types
from pyrogram.methods.invite_links.get_chat_admins_with_invite_links import (
    GetChatAdminsWithInviteLinks,
)

_CHAT_ID: Final[int] = -1001234567890


class FakeClient(GetChatAdminsWithInviteLinks):
    """A client that answers `messages.GetAdminsWithInvites` with the admins it was given."""

    def __init__(self, admins: List[raw.types.ChatAdminWithInvites]) -> None:
        self.admins = admins

    async def resolve_peer(self, peer_id: int) -> raw.types.InputPeerChannel:
        return raw.types.InputPeerChannel(channel_id=abs(peer_id), access_hash=0)

    async def invoke(
        self, query: raw.functions.messages.GetAdminsWithInvites
    ) -> raw.types.messages.ChatAdminsWithInvites:
        return raw.types.messages.ChatAdminsWithInvites(
            admins=self.admins,
            users=[
                raw.types.User(
                    id=admin.admin_id,
                    first_name=f"Admin {admin.admin_id}",
                    usernames=[],
                    restriction_reason=[],
                )
                for admin in self.admins
            ],
        )


@pytest.mark.asyncio
async def test_every_admin_is_parsed() -> None:
    # The call used to hand `types.List` a generator expression, and PEP 530 makes one
    #  holding an `await` an async generator: `list()` refused it with
    #  `TypeError: 'async_generator' object is not iterable`, so the method never returned.
    client = FakeClient(
        [
            raw.types.ChatAdminWithInvites(
                admin_id=7, invites_count=3, revoked_invites_count=1
            ),
            raw.types.ChatAdminWithInvites(
                admin_id=8, invites_count=0, revoked_invites_count=0
            ),
        ]
    )

    admins = await client.get_chat_admins_with_invite_links(_CHAT_ID)

    assert isinstance(admins, types.List)
    assert [admin.admin.id for admin in admins] == [7, 8]
    assert [admin.chat_invite_links_count for admin in admins] == [3, 0]


@pytest.mark.asyncio
async def test_a_chat_with_no_such_admin_answers_with_an_empty_list() -> None:
    admins = await FakeClient([]).get_chat_admins_with_invite_links(_CHAT_ID)

    assert admins == []
