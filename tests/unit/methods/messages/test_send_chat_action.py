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
from pyrogram.methods.messages.send_chat_action import SendChatAction, _ACTIONS


class FakeClient(SendChatAction):
    """A client that captures the raw action built for `messages.SetTyping`."""

    def __init__(self) -> None:
        self.captured = None

    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerUser(user_id=peer_id, access_hash=0)

    async def invoke(self, query: raw.functions.messages.SetTyping, **kwargs):
        self.captured = query.action
        return True


@pytest.mark.asyncio
@pytest.mark.parametrize("action", list(enums.ChatAction))
async def test_every_chat_action_resolves_to_its_raw_action(action) -> None:
    # `_ACTIONS` is a hand-written map from every `enums.ChatAction` member to its raw
    #  constructor; this walks the enum itself so a member added without a matching
    #  entry fails here instead of surfacing as a KeyError at call time.
    client = FakeClient()

    result = await client.send_chat_action(chat_id=7, action=action)

    assert result is True
    assert isinstance(client.captured, action.value)


def test_actions_map_covers_every_enum_member() -> None:
    assert set(_ACTIONS) == set(enums.ChatAction)
