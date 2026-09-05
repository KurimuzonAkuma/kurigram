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

from pyrogram import raw
from pyrogram.methods.contacts.add_contact import AddContact


class _Parser:
    async def parse(self, text, mode=None):
        return {"message": text, "entities": []}


class FakeClient(AddContact):
    """A client that records the raw `note` sent to `contacts.AddContact`."""

    def __init__(self) -> None:
        self.parse_mode = None
        self.parser = _Parser()
        self.written_note = None

    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerUser(user_id=7, access_hash=0)

    async def invoke(self, query: raw.functions.contacts.AddContact) -> raw.types.Updates:
        self.written_note = query.note

        return raw.types.Updates(
            updates=[],
            users=[raw.types.User(id=7, first_name="User 7", usernames=[], restriction_reason=[])],
            chats=[],
            date=0,
            seq=0,
        )


@pytest.mark.asyncio
async def test_note_is_written_with_the_client() -> None:
    # FormattedText.write() requires `client` to resolve mentions/parse_mode; calling it
    #  with no arguments raised `TypeError: write() missing 1 required positional argument`
    #  whenever a note was actually provided.
    client = FakeClient()

    user = await client.add_contact(7, "Foo", note="hello")

    assert user.id == 7
    assert isinstance(client.written_note, raw.types.TextWithEntities)
    assert client.written_note.text == "hello"


@pytest.mark.asyncio
async def test_no_note_skips_write() -> None:
    client = FakeClient()

    await client.add_contact(7, "Foo")

    assert client.written_note is None
