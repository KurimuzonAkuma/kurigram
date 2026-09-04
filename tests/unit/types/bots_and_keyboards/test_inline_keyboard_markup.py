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

"""`InlineKeyboardMarkup.write()` builds the constructors the current layer declares.

The expected names are read out of the generated schema rather than spelled out here, so a
layer that renames either constructor fails this test instead of silently going out on the
wire as the previous layer's shape.
"""

from typing import get_args

from pyrogram import raw, types


def declared_constructor(tl_type: type, *, field: str) -> str:
    """Name of the constructor the schema declares for a vector field of `tl_type`."""
    (forward_ref,) = get_args(tl_type.__init__.__annotations__[field])
    return forward_ref.__forward_arg__.rsplit(".", 1)[-1]


async def test_write_builds_the_constructors_the_schema_declares() -> None:
    markup = types.InlineKeyboardMarkup(
        [[types.InlineKeyboardButton("text", callback_data="data")]]
    )

    built = await markup.write(client=None)

    assert [type(row).__name__ for row in built.rows] == [
        declared_constructor(raw.types.ReplyInlineMarkup, field="rows")
    ]
    assert [type(button).__name__ for button in built.rows[0].buttons] == [
        declared_constructor(raw.types.KeyboardInlineButtonRow, field="buttons")
    ]
