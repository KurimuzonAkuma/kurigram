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

from typing import NamedTuple, Optional, Union

from pyrogram.filters import Filter


class UnboundArguments(NamedTuple):
    filters: Optional[Filter]
    group: int


def unbound_arguments(
    receiver: Optional[Filter],
    *,
    filters: Union[Filter, int, None],
    group: int,
) -> UnboundArguments:
    """Read what `@Client.on_*(...)` was given, whichever way it was written.

    The decorator is a method, so an unbound call shifts every positional argument one
    slot to the left: the filter lands in `self` and the group in `filters`. A call by
    keyword shifts nothing, and the two forms have to be told apart before either is read.
    """
    if isinstance(filters, int):
        return UnboundArguments(receiver, filters)

    return UnboundArguments(receiver if isinstance(receiver, Filter) else filters, group)
