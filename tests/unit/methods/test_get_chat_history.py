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

from typing import Any, AsyncIterator, List, Protocol

import pytest

from pyrogram import enums, types
from pyrogram.methods.messages import get_chat_history
from pyrogram.methods.messages.get_chat_history import GetChatHistory


class SetHistory(Protocol):
    def __call__(self, *chunks: List[types.Message]) -> None: ...


@pytest.fixture
def history(monkeypatch: pytest.MonkeyPatch) -> SetHistory:
    """Hand `get_chat_history()` the given chunks, one call after another, then nothing."""

    def set_history(*chunks: List[types.Message]) -> None:
        remaining = list(chunks)

        # The stand-in answers whatever `get_chunk()` is asked, so it takes the whole
        #  keyword signature without naming it.
        async def one_chunk(*args: Any, **kwargs: Any) -> List[types.Message]:
            return remaining.pop(0) if remaining else []

        monkeypatch.setattr(get_chat_history, "get_chunk", one_chunk)

    return set_history


def a_chat_of_every_kind() -> List[types.Message]:
    return [
        types.Message(id=1, empty=True),
        types.Message(id=2, service=enums.MessageServiceType.NEW_CHAT_MEMBERS),
        types.Message(id=3, text="a message"),
    ]


async def ids_of(messages: AsyncIterator[types.Message]) -> List[int]:
    return [message.id async for message in messages]


@pytest.mark.asyncio
async def test_every_message_comes_back_by_default(history: SetHistory) -> None:
    history(a_chat_of_every_kind())

    assert await ids_of(GetChatHistory().get_chat_history("a_chat")) == [1, 2, 3]


@pytest.mark.asyncio
async def test_skip_empty_leaves_out_the_deleted_messages(history: SetHistory) -> None:
    history(a_chat_of_every_kind())

    assert await ids_of(GetChatHistory().get_chat_history("a_chat", skip_empty=True)) == [2, 3]


@pytest.mark.asyncio
async def test_skip_service_leaves_out_the_service_messages(history: SetHistory) -> None:
    history(a_chat_of_every_kind())

    assert await ids_of(GetChatHistory().get_chat_history("a_chat", skip_service=True)) == [1, 3]


@pytest.mark.asyncio
async def test_both_flags_leave_only_the_messages_someone_wrote(history: SetHistory) -> None:
    history(a_chat_of_every_kind())

    messages = GetChatHistory().get_chat_history("a_chat", skip_empty=True, skip_service=True)

    assert await ids_of(messages) == [3]


@pytest.mark.asyncio
async def test_the_skipped_messages_do_not_count_towards_the_limit(history: SetHistory) -> None:
    history([
        types.Message(id=1, empty=True),
        types.Message(id=2, text="the first one"),
        types.Message(id=3, text="the second one"),
    ])

    messages = GetChatHistory().get_chat_history("a_chat", limit=2, skip_empty=True)

    assert await ids_of(messages) == [2, 3]


@pytest.mark.asyncio
async def test_a_chunk_that_is_skipped_whole_does_not_stop_the_walk(history: SetHistory) -> None:
    history(
        [types.Message(id=1, empty=True), types.Message(id=2, empty=True)],
        [types.Message(id=3, text="behind the deleted ones")],
    )

    messages = GetChatHistory().get_chat_history("a_chat", skip_empty=True)

    assert await ids_of(messages) == [3]
