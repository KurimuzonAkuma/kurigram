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

import asyncio

import pytest

from pyrogram.errors import FloodWait
from pyrogram.session.session import Session


class _Client:
    name = "test"


class _Session(Session):
    """A session whose `send()` always raises FloodWait, without the real transport."""

    def __init__(self, seconds) -> None:
        self.is_started = asyncio.Event()
        self.is_started.set()
        self.client = _Client()
        self.seconds = seconds
        self.send_calls = 0

    async def send(self, data, timeout=Session.WAIT_TIMEOUT):
        self.send_calls += 1
        raise FloodWait(self.seconds)


class _Query:
    QUALNAME = "test.Query"


@pytest.mark.asyncio
async def test_flood_wait_with_no_parsed_seconds_reraises() -> None:
    # FloodWait.seconds is Optional[int]: when Telegram's message doesn't match the
    #  expected pattern, `amount` ends up None, and `amount > sleep_threshold >= 0`
    #  raised TypeError instead of the intended FloodWait re-raise.
    session = _Session(seconds=None)

    with pytest.raises(FloodWait):
        await session.invoke(_Query())

    assert session.send_calls == 1


@pytest.mark.asyncio
async def test_flood_wait_past_threshold_reraises() -> None:
    session = _Session(seconds=999)

    with pytest.raises(FloodWait):
        await session.invoke(_Query(), sleep_threshold=10)

    assert session.send_calls == 1
