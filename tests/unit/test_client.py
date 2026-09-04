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

"""`Client.load_plugins()` reads a plugin package without tripping over what else lives in it.

A plugin module is ordinary user code, so anything at all can sit beside the decorated
functions: a database handle, a client object, a lazily built proxy.
"""

import asyncio
from pathlib import Path
from typing import Final

import pytest

from pyrogram import Client
from pyrogram.client import _plugin_handlers
from pyrogram.handlers import MessageHandler

_PLUGIN_SOURCE: Final[str] = '''
from pyrogram import Client


class AnyAttribute:
    """Answers every attribute with another instance, the way a PyMongo collection does."""

    def __getattr__(self, name):
        return AnyAttribute()


collection = AnyAttribute()


@Client.on_message()
async def greet(client, message):
    pass
'''


@pytest.fixture
def plugin_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    root: Path = tmp_path / "plugins"
    root.mkdir()
    (root / "greeter.py").write_text(_PLUGIN_SOURCE)

    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    return root.name


async def test_load_plugins_reads_past_an_attribute_proxy(plugin_root: str) -> None:
    client = Client(name="plugin_probe", in_memory=True)
    client.loop = asyncio.get_running_loop()
    client.plugins = {"root": plugin_root, "enabled": True}

    client.load_plugins()
    await asyncio.sleep(0)

    registered = [
        handler
        for group in client.dispatcher.groups.values()
        for handler in group
        if isinstance(handler, MessageHandler)
    ]

    assert len(registered) == 1


def test_plugin_handlers_ignores_what_is_not_a_pair_list() -> None:
    class AnyAttribute:
        def __getattr__(self, name: str) -> "AnyAttribute":
            return AnyAttribute()

    def undecorated() -> None:
        pass

    def decorated() -> None:
        pass

    decorated.handlers = [(MessageHandler(decorated), 0)]

    assert _plugin_handlers(AnyAttribute()) is None
    assert _plugin_handlers(undecorated) is None
    assert _plugin_handlers(decorated) == decorated.handlers
