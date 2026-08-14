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

import re
from io import BytesIO
from pathlib import Path

import pytest

from pyrogram import raw
from pyrogram.raw.core import TLObject, Vector

BLOCK = raw.types.PageBlockParagraph(text=raw.types.TextPlain(text="hi"))
PHOTO = raw.types.InputPhoto(id=1, access_hash=2, file_reference=b"")
# NOTE: `read()` gives a `flags.N?true` field `False`, never `None`, so the two `true` flags are
#       spelled out here — otherwise the objects compare unequal for a reason this file is not about.
USERNAME = raw.types.Username(username="name", editable=False, active=True)

# One case per sub-type the generator branches on, plus a function and a class whose vector
# lives in the second flags group. `build(None)` is the field never passed, `build([])` the
# empty list, `build(items)` a real value.
CASES = [
    pytest.param(
        lambda photos: raw.types.InputRichMessage(blocks=[BLOCK], photos=photos),
        [PHOTO],
        lambda message: message.photos,
        id="Vector<InputPhoto>"
    ),
    pytest.param(
        lambda usernames: raw.types.User(id=1, usernames=usernames),
        [USERNAME],
        lambda user: user.usernames,
        id="Vector<Username>-in-flags2"
    ),
    pytest.param(
        lambda slots: raw.functions.premium.ApplyBoost(peer=raw.types.InputPeerSelf(), slots=slots),
        [1, 2],
        lambda request: request.slots,
        id="Vector<int>-in-a-function"
    ),
    pytest.param(
        lambda users: raw.types.BusinessRecipients(users=users),
        [10, 20],
        lambda recipients: recipients.users,
        id="Vector<long>"
    ),
    pytest.param(
        lambda prefixes: raw.types.help.CountryCode(country_code="US", prefixes=prefixes),
        ["7", "8"],
        lambda country: country.prefixes,
        id="Vector<string>"
    ),
    pytest.param(
        lambda logout_tokens: raw.types.CodeSettings(logout_tokens=logout_tokens),
        [b"\x01\x02"],
        lambda settings: settings.logout_tokens,
        id="Vector<bytes>"
    )
]


@pytest.mark.parametrize(("build", "items", "read"), CASES)
def test_an_empty_vector_is_written_as_absent(build, items, read):
    assert build([]).write() == build(None).write()


@pytest.mark.parametrize(("build", "items", "read"), CASES)
def test_a_vector_with_items_is_still_written(build, items, read):
    written = build(items).write()

    assert written != build(None).write()
    assert read(TLObject.read(BytesIO(written))) == items


@pytest.mark.parametrize(
    "value",
    [lambda items: None, lambda items: [], lambda items: items],
    ids=["never-passed", "empty", "filled"]
)
@pytest.mark.parametrize(("build", "items", "read"), CASES)
def test_a_round_trip_is_byte_for_byte(build, items, read, value):
    written = build(value(items)).write()
    restored = TLObject.read(BytesIO(written))

    assert restored.write() == written


@pytest.mark.parametrize(("build", "items", "read"), CASES)
def test_an_empty_vector_does_not_eat_the_object_after_it(build, items, read):
    pair = Vector([build([]), build(items)])
    first, second = TLObject.read(BytesIO(pair))

    assert type(first) is type(second)
    assert read(first) == []
    assert read(second) == items


def test_an_empty_vector_does_not_eat_the_field_after_it():
    country = raw.types.help.CountryCode(country_code="US", prefixes=[], patterns=["+1 (###) ###"])
    restored = TLObject.read(BytesIO(country.write()))

    assert restored.prefixes == []
    assert restored.patterns == ["+1 (###) ###"]


def test_an_empty_vector_does_not_eat_a_field_from_the_next_flags_group():
    user = raw.types.User(id=1, restriction_reason=[], usernames=[USERNAME], lang_code="en")
    restored = TLObject.read(BytesIO(user.write()))

    assert restored.restriction_reason == []
    assert restored.lang_code == "en"
    assert restored.usernames == [USERNAME]


VECTOR_FIELD = re.compile(r"^        self\.(\w+) = \w+  # flags\d?\.\d+\?Vector<", re.MULTILINE)


def test_no_generated_class_writes_an_optional_vector_it_did_not_announce():
    checked = 0
    written_by_identity = []

    for path in sorted(Path(raw.__file__).parent.rglob("*.py")):
        source = path.read_text(encoding="utf-8")

        for name in VECTOR_FIELD.findall(source):
            checked += 1

            if f"if self.{name} is not None:" in source:
                written_by_identity.append(f"{path.name}: {name}")

    assert written_by_identity == []

    # The schema has 146 fields of this shape; a collector that stopped matching would otherwise
    # pass with an empty list.
    assert checked > 100
