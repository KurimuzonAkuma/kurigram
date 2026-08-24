import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

import pyrogram
from pyrogram.errors import ListenerStopped, ListenerTimeout
from pyrogram.filters import Filter
from pyrogram.handlers import CallbackQueryHandler, MessageHandler
from pyrogram.types import CallbackQuery, Chat, Message, User, ListenerTypes


@pytest.mark.asyncio
async def test_listen_and_message_handler():
    client = pyrogram.Client("test_session", in_memory=True)
    chat = Chat(id=123, type=pyrogram.enums.ChatType.PRIVATE)
    user = User(id=456, first_name="Test")
    msg = Message(id=1, chat=chat, from_user=user, text="Hello world")

    # Start listen in background task
    listen_task = asyncio.create_task(client.listen(chat_id=123, user_id=456))
    await asyncio.sleep(0.01)

    handler = MessageHandler(lambda c, m: None)
    match, listener = await handler.check_if_has_matching_listener(client, msg)
    assert match is True
    assert listener is not None

    # Resolve message via handler
    with pytest.raises(pyrogram.StopPropagation):
        await handler.resolve_future_or_callback(client, msg)

    received_msg = await listen_task
    assert received_msg.text == "Hello world"
    assert len(client.listeners[ListenerTypes.MESSAGE]) == 0


@pytest.mark.asyncio
async def test_listen_timeout():
    client = pyrogram.Client("test_session", in_memory=True)
    with pytest.raises(ListenerTimeout):
        await client.listen(chat_id=123, timeout=1)


@pytest.mark.asyncio
async def test_stop_listening():
    client = pyrogram.Client("test_session", in_memory=True)
    listen_task = asyncio.create_task(client.listen(chat_id=123))
    await asyncio.sleep(0.01)

    await client.stop_listening(chat_id=123)
    with pytest.raises(ListenerStopped):
        await listen_task


@pytest.mark.asyncio
async def test_chat_and_user_bound_methods():
    client = pyrogram.Client("test_session", in_memory=True)
    chat = Chat(id=123, client=client)
    user = User(id=456, client=client)

    client.send_message = AsyncMock(return_value=Message(id=1, text="Question"))

    listen_task = asyncio.create_task(chat.listen())
    await asyncio.sleep(0.01)
    assert len(client.listeners[ListenerTypes.MESSAGE]) == 1
    await client.stop_listening(chat_id=123)
    with pytest.raises(ListenerStopped):
        await listen_task

    listen_task2 = asyncio.create_task(user.listen())
    await asyncio.sleep(0.01)
    assert len(client.listeners[ListenerTypes.MESSAGE]) == 1
    await client.stop_listening(user_id=456)
    with pytest.raises(ListenerStopped):
        await listen_task2


@pytest.mark.asyncio
async def test_message_wait_for_click():
    client = pyrogram.Client("test_session", in_memory=True)
    chat = Chat(id=123)
    user = User(id=456)
    msg = Message(id=99, chat=chat, client=client)

    click_task = asyncio.create_task(msg.wait_for_click(from_user_id=456))
    await asyncio.sleep(0.01)

    query = CallbackQuery(id="q1", from_user=user, message=msg)
    handler = CallbackQueryHandler(lambda c, q: None)

    match, listener = await handler.check_if_has_matching_listener(client, query)
    assert match is True
    assert listener is not None

    with pytest.raises(pyrogram.StopPropagation):
        await handler.resolve_future_or_callback(client, query)

    res = await click_task
    assert res.id == "q1"
