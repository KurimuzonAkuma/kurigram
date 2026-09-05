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

from pyrogram.types.messages_and_media.message import Message


class _Chat:
    id = 42


class _Client:
    def __init__(self) -> None:
        self.captured = "not-called"

    async def send_game(self, **kwargs):
        self.captured = kwargs["effect_id"]
        return None


class _Message:
    chat = _Chat()
    id = 1
    message_thread_id = None

    def __init__(self, client: _Client) -> None:
        self._client = client


@pytest.mark.asyncio
async def test_reply_game_default_effect_id_is_none() -> None:
    # `effect_id: int = Optional[None]` evaluated at runtime to the NoneType class
    #  itself, not to None (Optional[None] collapses to NoneType): every call that
    #  omitted effect_id silently forwarded that class object to send_game().
    client = _Client()

    await Message.reply_game(_Message(client), "lumberjack")

    assert client.captured is None


@pytest.mark.asyncio
async def test_answer_game_default_effect_id_is_none() -> None:
    client = _Client()

    await Message.answer_game(_Message(client), "lumberjack")

    assert client.captured is None
