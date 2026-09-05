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

from pathlib import Path

import pytest

from pyrogram.storage.sqlite_storage import SQLiteStorage


@pytest.mark.asyncio
async def test_conn_property_round_trips_the_connection() -> None:
    # self.conn moved from a plain attribute (declared non-Optional via a
    #  `# type:` comment but assigned None in __init__) to a property backed by
    #  self._conn, so open()/close() and every query still have to see the same
    #  connection object through the ordinary self.conn read/write syntax.
    storage = SQLiteStorage("test", Path("."), in_memory=True)

    await storage.open()
    assert await storage.is_bot() is None

    await storage.date(0)
    assert await storage.date() == 0

    await storage.close()


def test_conn_raises_before_open() -> None:
    storage = SQLiteStorage("test", Path("."), in_memory=True)

    with pytest.raises(RuntimeError):
        _ = storage.conn
