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

import pytest

from pyrogram import raw, types

_USERS = {
    7: raw.types.User(id=7, first_name="User 7", usernames=[], restriction_reason=[]),
}


@pytest.mark.asyncio
async def test_chosen_inline_result_with_geo_does_not_crash() -> None:
    # types.Location doesn't accept a `client` argument at all (it isn't an Update
    #  subclass), so passing one raised `TypeError: __init__() got an unexpected keyword
    #  argument 'client'` for every chosen inline result that carried a location.
    update = raw.types.UpdateBotInlineSend(
        user_id=7,
        query="q",
        geo=raw.types.GeoPoint(long=1.5, lat=2.5, access_hash=0),
        id="result-id",
    )

    result = await types.ChosenInlineResult._parse(None, update, _USERS)

    assert result.location.longitude == 1.5
    assert result.location.latitude == 2.5


@pytest.mark.asyncio
async def test_inline_query_with_geo_does_not_crash() -> None:
    update = raw.types.UpdateBotInlineQuery(
        query_id=1,
        user_id=7,
        query="q",
        geo=raw.types.GeoPoint(long=1.5, lat=2.5, access_hash=0),
        offset="",
    )

    query = await types.InlineQuery._parse(None, update, _USERS)

    assert query.location.longitude == 1.5
    assert query.location.latitude == 2.5
