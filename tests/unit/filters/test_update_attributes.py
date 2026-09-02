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

import inspect
from datetime import datetime
from typing import Optional

import pytest

from pyrogram import enums, filters, types
from pyrogram.types import (
    CallbackQuery,
    Chat,
    ChatJoinRequest,
    ChatMemberUpdated,
    InlineQuery,
    Message,
    Poll,
    PreCheckoutQuery,
    Update,
    User,
)

# No filter under test reads the client argument.
CLIENT = None

DATE = datetime(2025, 1, 1)

PRIVATE = Chat(id=42, type=enums.ChatType.PRIVATE, username="someone")
CHANNEL = Chat(id=-100, type=enums.ChatType.CHANNEL)
SAVED_MESSAGES = Chat(id=7, type=enums.ChatType.PRIVATE)

SOMEONE = User(id=42, username="someone")
A_BOT = User(id=42, username="someone", is_bot=True)
MYSELF = User(id=7, is_self=True)


def in_private(update_type, **kwargs):
    """Build an update of `update_type` that happens in `PRIVATE`."""
    if update_type is Message:
        return Message(id=1, chat=PRIVATE, **kwargs)

    if update_type is CallbackQuery:
        return CallbackQuery(id="1", message=Message(id=1, chat=PRIVATE), **kwargs)

    return update_type(chat=PRIVATE, date=DATE, **kwargs)


def inline_query(from_user: User) -> InlineQuery:
    return InlineQuery(id="1", from_user=from_user, query="", offset="", chat_type=enums.ChatType.PRIVATE)


def pre_checkout_query(from_user: User) -> PreCheckoutQuery:
    return PreCheckoutQuery(id="1", from_user=from_user, currency="XTR", total_amount=1, invoice_payload="x")


def poll() -> Poll:
    return Poll(id="1", options=[], is_closed=False)


WITH_A_CHAT = [
    pytest.param(in_private(Message), id="message"),
    pytest.param(in_private(CallbackQuery, from_user=SOMEONE), id="callback_query"),
    pytest.param(in_private(ChatJoinRequest, from_user=SOMEONE), id="chat_join_request"),
    pytest.param(in_private(ChatMemberUpdated, from_user=SOMEONE), id="chat_member_updated"),
]

WITHOUT_A_CHAT = [
    pytest.param(inline_query(SOMEONE), id="inline_query"),
    pytest.param(pre_checkout_query(SOMEONE), id="pre_checkout_query"),
    pytest.param(poll(), id="poll"),
    pytest.param(CallbackQuery(id="1", from_user=SOMEONE), id="callback_query_on_an_inline_message"),
]

FROM_A_BOT = [
    pytest.param(Message(id=1, chat=PRIVATE, from_user=A_BOT), id="message"),
    pytest.param(CallbackQuery(id="1", from_user=A_BOT), id="callback_query"),
    pytest.param(inline_query(A_BOT), id="inline_query"),
    pytest.param(pre_checkout_query(A_BOT), id="pre_checkout_query"),
]

FROM_MYSELF = [
    pytest.param(Message(id=1, chat=PRIVATE, from_user=MYSELF), id="message"),
    pytest.param(CallbackQuery(id="1", from_user=MYSELF), id="callback_query"),
    pytest.param(inline_query(MYSELF), id="inline_query"),
    pytest.param(pre_checkout_query(MYSELF), id="pre_checkout_query"),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("update", WITH_A_CHAT)
async def test_chat_filters_read_the_chat_of_any_update(update):
    assert await filters.private(CLIENT, update)
    assert await filters.chat(42)(CLIENT, update)
    assert await filters.chat("someone")(CLIENT, update)
    assert not await filters.channel(CLIENT, update)


@pytest.mark.asyncio
@pytest.mark.parametrize("update", WITHOUT_A_CHAT)
async def test_an_update_with_no_chat_does_not_match_rather_than_raising(update):
    assert not await filters.private(CLIENT, update)
    assert not await filters.group(CLIENT, update)
    assert not await filters.channel(CLIENT, update)
    assert not await filters.forum(CLIENT, update)
    assert not await filters.admin(CLIENT, update)
    assert not await filters.chat(42)(CLIENT, update)


@pytest.mark.asyncio
@pytest.mark.parametrize("update", FROM_A_BOT)
async def test_sender_filters_read_the_sender_of_any_update(update):
    assert await filters.bot(CLIENT, update)
    assert await filters.user(42)(CLIENT, update)
    assert await filters.user("someone")(CLIENT, update)
    assert not await filters.user("nobody")(CLIENT, update)
    assert not await filters.me(CLIENT, update)


@pytest.mark.asyncio
@pytest.mark.parametrize("update", FROM_MYSELF)
async def test_me_reads_the_sender_of_any_update(update):
    assert await filters.me(CLIENT, update)
    assert await filters.user("me")(CLIENT, update)
    assert not await filters.bot(CLIENT, update)


@pytest.mark.asyncio
async def test_an_update_that_cannot_be_outgoing_is_incoming():
    assert await filters.incoming(CLIENT, poll())
    assert not await filters.outgoing(CLIENT, poll())
    assert not await filters.sender_chat(CLIENT, poll())


@pytest.mark.asyncio
async def test_message_filters_are_unchanged():
    outgoing_message = Message(id=1, chat=CHANNEL, sender_chat=CHANNEL, outgoing=True)

    assert await filters.channel(CLIENT, outgoing_message)
    assert await filters.outgoing(CLIENT, outgoing_message)
    assert await filters.sender_chat(CLIENT, outgoing_message)
    assert not await filters.incoming(CLIENT, outgoing_message)
    assert await filters.chat(-100)(CLIENT, outgoing_message)


@pytest.mark.asyncio
async def test_chat_me_is_saved_messages_and_nothing_else():
    """`filters.chat("me")` means the chat whose id is your own user id.

    It used to test the sender instead (`is_self and not outgoing`), which is
    also true of an update you caused in a chat that is not Saved Messages.
    """
    assert await filters.chat("me")(CLIENT, Message(id=1, chat=SAVED_MESSAGES, from_user=MYSELF))
    assert await filters.chat("self")(CLIENT, Message(id=1, chat=SAVED_MESSAGES, from_user=MYSELF))

    in_a_supergroup = CallbackQuery(
        id="1",
        from_user=MYSELF,
        message=Message(id=1, chat=Chat(id=-1001, type=enums.ChatType.SUPERGROUP)),
    )

    assert not await filters.chat("me")(CLIENT, in_a_supergroup)


@pytest.mark.asyncio
async def test_me_added_to_the_container_after_the_fact_still_matches():
    """The container is public, so an alias can enter it without `__init__` seeing it."""
    in_saved_messages = Message(id=1, chat=SAVED_MESSAGES, from_user=MYSELF)

    users = filters.user()
    users.add("self")

    chats = filters.chat()
    chats.add("self")

    assert await users(CLIENT, in_saved_messages)
    assert await chats(CLIENT, in_saved_messages)


UPDATE_TYPES = [
    one for one in vars(types).values()
    if inspect.isclass(one) and issubclass(one, Update) and one is not Update
]


def carries(update_type, field: str) -> bool:
    """Whether `update_type` answers `field`, as an `__init__` argument or as a property.

    The property is looked up in the class dictionaries along the MRO rather than read off
    the class, so it is found as the descriptor it is instead of being evaluated.
    """
    if field in inspect.signature(update_type.__init__).parameters:
        return True

    return any(isinstance(vars(one).get(field), property) for one in update_type.__mro__)


@pytest.mark.parametrize(
    ("field", "declared"),
    [
        ("from_user", filters._WITH_A_SENDER),
        ("chat", filters._WITH_A_CHAT),
        ("sender_chat", filters._WITH_A_SENDER_CHAT),
        ("outgoing", filters._CAN_BE_OUTGOING),
        ("message", filters._WITH_A_MESSAGE),
        ("user", filters._WITH_A_SENDER_NAMED_USER),
        ("actor_chat", filters._WITH_A_SENDER_CHAT_NAMED_ACTOR_CHAT),
        ("boost", filters._WITH_A_BOOSTER),
    ],
)
def test_the_filters_name_every_update_type_that_carries_the_field(field, declared):
    """The filters dispatch on these tuples, so an update type missing from one is invisible.

    Adding a field to an update type and forgetting the tuple here is a silent failure --
    the filter keeps answering "not applicable" for an update that does have an answer.
    """
    assert {one.__name__ for one in UPDATE_TYPES if carries(one, field)} == {
        one.__name__ for one in declared
    }


def test_the_update_base_class_declares_no_fields():
    """The filters read these off the concrete update, never off a default on `Update`.

    A default on the base would answer for every update type at once, and the answer
    would be wrong: an inline query would report a chat of `None`, as if it were an
    update that happens in a chat and simply does not know which one.
    """
    for name in ("from_user", "chat", "sender_chat", "outgoing"):
        assert not hasattr(Update, name)


A_TOPIC = types.ForumTopic(id=13)

FROM_THE_LINKED_CHANNEL = {
    "sender_chat": CHANNEL,
    "forward_origin": types.MessageOriginChannel(chat=CHANNEL, message_id=1),
}


def business_message() -> Message:
    return Message(id=1, chat=PRIVATE, business_connection_id="a_connection")


@pytest.mark.asyncio
async def test_business_reads_the_message_the_update_is_about():
    assert await filters.business(CLIENT, business_message())
    assert await filters.business(CLIENT, CallbackQuery(id="1", from_user=SOMEONE, message=business_message()))
    assert not await filters.business(CLIENT, Message(id=1, chat=PRIVATE))


@pytest.mark.asyncio
async def test_linked_channel_reads_the_message_the_update_is_about():
    forwarded = Message(id=1, chat=CHANNEL, **FROM_THE_LINKED_CHANNEL)

    assert await filters.linked_channel(CLIENT, forwarded)
    assert await filters.linked_channel(CLIENT, CallbackQuery(id="1", from_user=SOMEONE, message=forwarded))
    assert not await filters.linked_channel(CLIENT, Message(id=1, chat=CHANNEL))


@pytest.mark.asyncio
async def test_topic_reads_the_message_the_update_is_about():
    in_a_topic = Message(id=1, chat=PRIVATE, topic=A_TOPIC)

    assert await filters.topic(13)(CLIENT, in_a_topic)
    assert await filters.topic(13)(CLIENT, CallbackQuery(id="1", from_user=SOMEONE, message=in_a_topic))
    assert not await filters.topic(1)(CLIENT, in_a_topic)
    assert not await filters.topic(13)(CLIENT, Message(id=1, chat=PRIVATE))


@pytest.mark.asyncio
@pytest.mark.parametrize("update", WITHOUT_A_CHAT)
async def test_an_update_with_no_message_does_not_match_rather_than_raising(update):
    """These three read a field that only `Message` has.

    They used to take it off whatever the handler passed them, so a callback query or an
    inline query answered with `AttributeError: 'CallbackQuery' object has no attribute
    'business_connection_id'` instead of not matching.
    """
    assert not await filters.business(CLIENT, update)
    assert not await filters.linked_channel(CLIENT, update)
    assert not await filters.topic(13)(CLIENT, update)


def test_callback_query_chat_follows_its_message():
    assert CallbackQuery(id="1", from_user=SOMEONE).chat is None
    assert in_private(CallbackQuery, from_user=SOMEONE).chat.id == 42


def test_callback_query_chat_stays_out_of_the_serialized_form():
    """`chat` is derived, so it must not show up next to `message` in the output.

    `Object.default()` and `Object.__repr__()` walk `__dict__`, and `bind()`
    documents `eval(repr(obj))` as supported, so an attribute here would repeat the
    whole chat in the JSON and feed `__init__` a keyword it does not take.
    """
    query = in_private(CallbackQuery, from_user=SOMEONE)

    assert "chat" not in query.__dict__
    assert repr(query).count("Chat(") == 1


def a_reaction(
    *,
    user: Optional[User] = None,
    actor_chat: Optional[Chat] = None,
) -> types.MessageReactionUpdated:
    return types.MessageReactionUpdated(
        chat=CHANNEL,
        message_id=1,
        date=DATE,
        old_reaction=[],
        new_reaction=[],
        user=user,
        actor_chat=actor_chat,
    )


def a_boost(from_user: User) -> types.ChatBoostUpdated:
    return types.ChatBoostUpdated(
        chat=CHANNEL,
        boost=types.ChatBoost(id="1", date=DATE, expire_date=DATE, multiplier=1, from_user=from_user),
    )


@pytest.mark.asyncio
async def test_a_user_status_update_is_its_own_sender() -> None:
    """`UpdateUserStatus` is parsed into the `User` it is about and nothing else.

    So `@app.on_user_status(filters.user(42))` had no sender to read and never fired,
    even though the update names the user it is about.
    """
    assert await filters.user(42)(CLIENT, SOMEONE)
    assert await filters.user("someone")(CLIENT, SOMEONE)
    assert not await filters.user("nobody")(CLIENT, SOMEONE)

    assert await filters.me(CLIENT, MYSELF)
    assert await filters.bot(CLIENT, A_BOT)


@pytest.mark.asyncio
async def test_a_reaction_reads_the_user_that_reacted() -> None:
    assert await filters.user(42)(CLIENT, a_reaction(user=SOMEONE))
    assert await filters.user("someone")(CLIENT, a_reaction(user=SOMEONE))
    assert await filters.bot(CLIENT, a_reaction(user=A_BOT))
    assert not await filters.user(42)(CLIENT, a_reaction(actor_chat=CHANNEL))


@pytest.mark.asyncio
async def test_a_reaction_left_anonymously_reads_the_chat_it_was_left_as() -> None:
    assert await filters.sender_chat(CLIENT, a_reaction(actor_chat=CHANNEL))
    assert not await filters.sender_chat(CLIENT, a_reaction(user=SOMEONE))

    # The chat the message lives in keeps answering, whoever reacted.
    assert await filters.channel(CLIENT, a_reaction(user=SOMEONE))


@pytest.mark.asyncio
async def test_a_boost_reads_the_user_that_boosted() -> None:
    assert await filters.user(42)(CLIENT, a_boost(SOMEONE))
    assert await filters.user("someone")(CLIENT, a_boost(SOMEONE))
    assert await filters.me(CLIENT, a_boost(MYSELF))
    assert not await filters.user(42)(CLIENT, types.ChatBoostUpdated(chat=CHANNEL, boost=None))


@pytest.mark.asyncio
async def test_a_callback_query_reads_the_sender_chat_of_its_message() -> None:
    """A button under a channel post: the post has a sender chat, the query has none of its own."""
    posted_as_the_channel = Message(id=1, chat=CHANNEL, sender_chat=CHANNEL)

    assert await filters.sender_chat(CLIENT, CallbackQuery(id="1", from_user=SOMEONE, message=posted_as_the_channel))
    assert not await filters.sender_chat(CLIENT, in_private(CallbackQuery, from_user=SOMEONE))
    assert not await filters.sender_chat(CLIENT, CallbackQuery(id="1", from_user=SOMEONE))


def test_the_filters_name_every_update_type_that_is_a_user() -> None:
    """`_IS_ITS_OWN_SENDER` cannot be checked by field, the way the tuples above are."""
    assert {one.__name__ for one in UPDATE_TYPES if issubclass(one, User)} == {
        one.__name__ for one in filters._IS_ITS_OWN_SENDER
    }
