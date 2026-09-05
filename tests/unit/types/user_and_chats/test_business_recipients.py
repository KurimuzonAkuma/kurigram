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


@pytest.mark.asyncio
async def test_no_users_lookup_dict_does_not_crash() -> None:
    # `users` (the lookup dict) is declared Optional and defaults to None; indexing it
    #  with `users[i]` used to run unconditionally whenever `recipients.users` was
    #  non-empty, regardless of whether a lookup dict was actually supplied.
    recipients = raw.types.BusinessRecipients(users=[7, 8])

    parsed = await types.BusinessRecipients._parse(None, recipients, users=None)

    assert parsed.users is None


@pytest.mark.asyncio
async def test_users_are_resolved_from_the_lookup_dict() -> None:
    recipients = raw.types.BusinessRecipients(users=[7])
    users = {
        7: raw.types.User(id=7, first_name="User 7", usernames=[], restriction_reason=[]),
    }

    parsed = await types.BusinessRecipients._parse(None, recipients, users=users)

    assert parsed.users is not None
    assert [user.id for user in parsed.users] == [7]
