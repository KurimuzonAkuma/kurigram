import asyncio
from pathlib import Path
import sys
import types
from unittest.mock import MagicMock
import pytest
from pyrogram import Client
from pyrogram.dispatcher import Dispatcher
from pyrogram.handlers import MessageHandler
from pyrogram.storage import SQLiteStorage


@pytest.mark.asyncio
async def test_dispatcher_handles_none_parser():
    client = MagicMock(spec=Client)
    client.executor = None
    client.loop = asyncio.get_running_loop()
    client.workers = 1
    client.no_updates = False
    client.stop_handler = None

    dispatcher = Dispatcher(client)

    class DummyUpdate:
        pass

    async def none_parser(update, users, chats):
        return None

    dispatcher.update_parsers[DummyUpdate] = none_parser

    lock = asyncio.Lock()
    worker_task = asyncio.create_task(dispatcher.handler_worker(lock))

    await dispatcher.updates_queue.put((DummyUpdate(), {}, {}))
    await dispatcher.updates_queue.put(None)

    await asyncio.wait_for(worker_task, timeout=2.0)
    assert worker_task.done()
    assert worker_task.exception() is None


@pytest.mark.asyncio
async def test_load_plugins_handles_mongo_like_collections(monkeypatch):
    client = Client(name="test_bot", in_memory=True)
    client.loop = asyncio.get_running_loop()
    client.plugins = {"root": "fake_plugins", "enabled": True}

    # Simulate an object with dynamic handlers attribute (like Motor / PyMongo collection)
    class DynamicCollection:
        def __getattr__(self, name):
            return DynamicCollection()

    mock_module = types.ModuleType("fake_plugins.mod")
    mock_module.collection = DynamicCollection()

    async def sample_fn(cli, msg):
        pass

    handler = MessageHandler(sample_fn)
    sample_fn.handlers = [(handler, 0)]
    mock_module.real_func = sample_fn

    monkeypatch.setitem(sys.modules, "fake_plugins.mod", mock_module)
    monkeypatch.setattr("pathlib.Path.rglob", lambda self, pattern: [Path("fake_plugins/mod.py")])

    # Should not raise TypeError: 'DynamicCollection' object is not iterable
    client.load_plugins()
    await asyncio.sleep(0.05)
    assert 0 in client.dispatcher.groups
    assert handler in client.dispatcher.groups[0]


@pytest.mark.asyncio
async def test_sqlite_storage_closed_resilience():
    storage = SQLiteStorage("test_resilience", workdir=Path("/tmp"), in_memory=True)
    await storage.open()
    assert storage.conn is not None

    await storage.close()
    assert storage.conn is None

    # Methods must not crash after close
    await storage.save()
    await storage.update_peers([])
    await storage.update_usernames([])
    assert await storage.get_update_states() == []
    await storage.set_update_state([])
    await storage.delete_update_state(1)
    await storage.close()
