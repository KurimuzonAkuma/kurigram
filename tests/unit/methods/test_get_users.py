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


from typing import List, Union

import pytest

from pyrogram import raw
from pyrogram.methods.users.get_users import GetUsers


class Answerer(GetUsers):
    """A client that answers `users.GetUsers` with a fixed vector and resolves any peer."""

    def __init__(self, answer: List["raw.base.User"]) -> None:
        self.answer = answer

    async def resolve_peer(self, peer_id: Union[int, str]) -> "raw.types.InputUser":
        return raw.types.InputUser(user_id=1, access_hash=0)

    async def invoke(self, query: "raw.core.TLObject") -> List["raw.base.User"]:
        return self.answer


def a_user(user_id: int) -> "raw.types.User":
    # `usernames` and `restriction_reason` are `flags.N?Vector<...>`, and the generated `read()`
    #  gives an absent vector back as `[]`. `User._parse()` iterates both without guarding, so a
    #  hand-built `raw.types.User` has to spell out what the wire implies.
    return raw.types.User(
        id=user_id,
        first_name=f"User {user_id}",
        usernames=[],
        restriction_reason=[]
    )


@pytest.mark.asyncio
async def test_a_single_identifier_that_is_no_user_gives_nothing_back() -> None:
    # Telegram answers with an empty vector for an id that belongs to a channel, a chat or a
    #  peer this account cannot see. Indexing into it raised `IndexError` out of the method body.
    assert await Answerer([]).get_users("a_channel_username") is None


@pytest.mark.asyncio
async def test_a_single_identifier_still_gives_its_user_back() -> None:
    user = await Answerer([a_user(42)]).get_users(42)

    assert user.id == 42


@pytest.mark.asyncio
async def test_a_list_of_identifiers_that_are_no_users_gives_an_empty_list() -> None:
    users = await Answerer([]).get_users(["a_channel_username"])

    assert users == []


@pytest.mark.asyncio
async def test_a_list_keeps_only_the_users_telegram_answered_with() -> None:
    users = await Answerer([a_user(1), a_user(2)]).get_users([1, 2, 3])

    assert [user.id for user in users] == [1, 2]


@pytest.mark.asyncio
async def test_a_deleted_account_arrives_as_nothing() -> None:
    # `userEmpty` is what the server sends for an account that no longer exists; `User._parse()`
    #  turns it into `None`, and that is what the single-identifier path has always returned.
    assert await Answerer([raw.types.UserEmpty(id=42)]).get_users(42) is None
