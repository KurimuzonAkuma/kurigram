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
from pyrogram.methods.stories.edit_story_privacy import EditStoryPrivacy


class _InvokeCalled(Exception):
    """Raised by the fake `invoke` once reached, carrying the built query for inspection."""

    def __init__(self, query) -> None:
        self.query = query


class FakeClient(EditStoryPrivacy):
    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerUser(user_id=peer_id, access_hash=0)

    async def invoke(self, query: raw.functions.stories.EditStory):
        raise _InvokeCalled(query)


@pytest.mark.asyncio
async def test_selected_users_without_allowed_users_does_not_crash() -> None:
    # `for user in allowed_users` iterated `allowed_users` unconditionally, so
    #  SELECTED_USERS with no `allowed_users` raised
    #  `TypeError: 'NoneType' object is not iterable` instead of sending an empty rule set.
    client = FakeClient()

    with pytest.raises(_InvokeCalled) as exc_info:
        await client.edit_story_privacy(
            7, 1, privacy=enums.StoriesPrivacyRules.SELECTED_USERS
        )

    assert exc_info.value.query.privacy_rules == []


@pytest.mark.asyncio
async def test_selected_users_with_allowed_users() -> None:
    client = FakeClient()

    with pytest.raises(_InvokeCalled) as exc_info:
        await client.edit_story_privacy(
            7,
            1,
            privacy=enums.StoriesPrivacyRules.SELECTED_USERS,
            allowed_users=[123],
        )

    rules = exc_info.value.query.privacy_rules
    assert len(rules) == 1
    assert isinstance(rules[0], raw.types.InputPrivacyValueAllowUsers)
