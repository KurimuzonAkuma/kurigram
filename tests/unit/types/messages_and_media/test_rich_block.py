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

from typing import Optional

import pytest

from pyrogram import raw, types


async def _parse(block: "raw.base.PageBlock") -> "types.RichBlock":
    return await types.RichBlock._parse(None, block, {}, {}, None, {}, {})


@pytest.mark.parametrize(
    ("collapsed", "expected"),
    [
        pytest.param(True, True, id="collapsed"),
        pytest.param(None, None, id="not-collapsed"),
    ],
)
async def test_a_blockquote_keeps_the_flag_the_schema_carries(
    collapsed: Optional[bool],
    *,
    expected: Optional[bool],
) -> None:
    parsed = await _parse(
        raw.types.PageBlockBlockquote(
            text=raw.types.TextPlain(text="quoted"),
            caption=raw.types.TextEmpty(),
            collapsed=collapsed,
        )
    )

    assert parsed.expandable is expected


async def test_the_nested_blockquote_constructor_carries_no_flag() -> None:
    parsed = await _parse(
        raw.types.PageBlockBlockquoteBlocks(
            blocks=[raw.types.PageBlockDivider()],
            caption=raw.types.TextEmpty(),
        )
    )

    assert parsed.expandable is None
