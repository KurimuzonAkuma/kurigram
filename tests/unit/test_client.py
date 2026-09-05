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
import logging
from pathlib import Path
from typing import Final, Protocol

import pytest

from pyrogram import Client, filters
from pyrogram.client import _plugin_handlers
from pyrogram.handlers import MessageHandler

_PLUGIN_SOURCE: Final[str] = """
from pyrogram import Client


class AnyAttribute:
    # Answers every attribute with another instance, the way a PyMongo collection does.

    def __getattr__(self, name):
        return AnyAttribute()


collection = AnyAttribute()


@Client.on_message()
async def greet(client, message):
    pass
"""


_KEYWORD_PLUGIN_SOURCE: Final[str] = """
from pyrogram import Client, filters


@Client.on_message(filters=filters.text, group=1)
async def greet(client, message):
    pass
"""

_REFUSED_PLUGIN_SOURCE: Final[str] = """
async def greet(client, message):
    pass


greet.handlers = [("not a handler", 0)]
"""


class PluginWriter(Protocol):
    def __call__(self, package: str, *, source: str) -> str: ...


@pytest.fixture
def write_plugin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> PluginWriter:
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    # Each test needs a package of its own: `import_module` caches by name, so a second
    #  package sharing a name resolves to the first one's files.
    def _write(package: str, *, source: str) -> str:
        root: Path = tmp_path / package
        root.mkdir()
        (root / "handlers.py").write_text(source)

        return package

    return _write


def _plugin_client(root: str) -> Client:
    client = Client(name="plugin_probe", in_memory=True)
    client.loop = asyncio.get_event_loop()
    client.plugins = {"root": root, "enabled": True}

    return client


async def test_load_plugins_reads_past_an_attribute_proxy(write_plugin: PluginWriter) -> None:
    client = _plugin_client(write_plugin("proxy_plugins", source=_PLUGIN_SOURCE))

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


async def test_load_plugins_registers_a_handler_declared_by_keyword(write_plugin: PluginWriter) -> None:
    client = _plugin_client(write_plugin("keyword_plugins", source=_KEYWORD_PLUGIN_SOURCE))

    client.load_plugins()
    await asyncio.sleep(0)

    (handler,) = client.dispatcher.groups[1]

    assert isinstance(handler, MessageHandler)
    assert handler.filters is filters.text


async def test_load_plugins_reports_the_pair_it_refuses(
    write_plugin: PluginWriter,
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = _plugin_client(write_plugin("refused_plugins", source=_REFUSED_PLUGIN_SOURCE))

    with caplog.at_level(logging.WARNING, logger="pyrogram.client"):
        client.load_plugins()
        await asyncio.sleep(0)

    assert client.dispatcher.groups == {}
    assert "greet" in caplog.text
