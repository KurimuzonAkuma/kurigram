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
from typing import Final, Optional

import pytest

import pyrogram
from pyrogram.session.session import Session, SessionState

_DC_ID: Final[int] = 2
_PORT: Final[int] = 443
_AUTH_KEY: Final[bytes] = bytes(256)
_PACKET: Final[bytes] = b"one packet"

# Long enough that a `stop()` which does not wait would have returned several times
#  over, short enough to keep the suite quick.
_NOT_DONE_TIMEOUT: Final[float] = 0.1

# What `Session.STOP_TIMEOUT` is replaced with, so a test of the cancelling path does
#  not sit through the real grace period.
_SHORT_STOP_TIMEOUT: Final[float] = 0.05


class StubConnection:
    def __init__(self) -> None:
        self.closed = asyncio.Event()
        self.packets = [_PACKET]

    async def recv(self) -> Optional[bytes]:
        if self.packets:
            return self.packets.pop()

        await self.closed.wait()
        return None

    async def close(self) -> None:
        self.closed.set()


def _started_session() -> Session:
    client = pyrogram.Client("test", api_id=1, api_hash="0" * 32, in_memory=True)
    session = Session(client, _DC_ID, "127.0.0.1", _PORT, _AUTH_KEY, test_mode=True)

    session.connection = StubConnection()
    session._state = SessionState.STARTED
    session.is_started.set()

    return session


async def test_stop_waits_for_the_packet_it_is_still_handling() -> None:
    session = _started_session()

    release = asyncio.Event()
    handled: bool = False

    async def handle_packet(packet: bytes) -> None:
        nonlocal handled

        await release.wait()
        handled = True

    session.handle_packet = handle_packet
    session.recv_task = session.client.loop.create_task(session.recv_worker())

    await asyncio.sleep(0)

    stopping = asyncio.ensure_future(session.stop())

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(asyncio.shield(stopping), _NOT_DONE_TIMEOUT)

    assert not handled

    release.set()
    await stopping

    assert handled
    assert session.pending_tasks == set()


async def test_stop_cancels_a_packet_that_will_not_finish(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(Session, "STOP_TIMEOUT", _SHORT_STOP_TIMEOUT)

    session = _started_session()

    async def handle_packet(packet: bytes) -> None:
        await asyncio.Event().wait()

    session.handle_packet = handle_packet
    session.recv_task = session.client.loop.create_task(session.recv_worker())

    await asyncio.sleep(0)

    handling = next(iter(session.pending_tasks))

    await session.stop()

    assert handling.cancelled()
    assert session.pending_tasks == set()


async def test_a_finished_task_leaves_the_pending_set() -> None:
    session = _started_session()

    task = session._create_tracked_task(asyncio.sleep(0))

    assert session.pending_tasks == {task}

    await task
    await asyncio.sleep(0)

    assert session.pending_tasks == set()
