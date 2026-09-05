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

from typing import List

import pytest

from pyrogram import raw, types
from pyrogram.methods.premium.get_boosts import GetBoosts


class FakeClient(GetBoosts):
    """A client that answers `premium.GetMyBoosts` with the boosts it was given."""

    def __init__(self, my_boosts: List[raw.types.MyBoost]) -> None:
        self.my_boosts = my_boosts

    async def invoke(
        self, query: raw.functions.premium.GetMyBoosts
    ) -> raw.types.premium.MyBoosts:
        return raw.types.premium.MyBoosts(
            my_boosts=self.my_boosts,
            chats=[],
            users=[
                raw.types.User(
                    id=abs(boost.peer.user_id),
                    first_name=f"User {boost.peer.user_id}",
                    usernames=[],
                    restriction_reason=[],
                )
                for boost in self.my_boosts
            ],
        )


@pytest.mark.asyncio
async def test_every_boost_is_parsed() -> None:
    # `types.List` handed a generator expression that yields awaits used to be an async
    #  generator (PEP 530): `list()` refused it with `TypeError: 'async_generator' object
    #  is not iterable`, so `get_boosts()` never returned.
    client = FakeClient(
        [
            raw.types.MyBoost(
                slot=1,
                peer=raw.types.PeerUser(user_id=7),
                date=1000,
                expires=2000,
            ),
            raw.types.MyBoost(
                slot=2,
                peer=raw.types.PeerUser(user_id=8),
                date=1500,
                expires=2500,
            ),
        ]
    )

    boosts = await client.get_boosts()

    assert isinstance(boosts, types.List)
    assert [boost.slot for boost in boosts] == [1, 2]
    assert [boost.chat.id for boost in boosts] == [7, 8]


@pytest.mark.asyncio
async def test_no_boosts_answers_with_an_empty_list() -> None:
    boosts = await FakeClient([]).get_boosts()

    assert boosts == []
