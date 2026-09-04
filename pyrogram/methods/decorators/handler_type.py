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

from typing import Callable, TypeVar

# Every handler decorator returns the function it was handed, unchanged. Binding the
#  parameter and the return to one type variable is what carries the callback's own
#  signature through: `def decorator(func: Callable) -> Callable` erased it, so a
#  decorated handler was `Any` to a type checker and `handler(1, 2, 3, 4)` passed.
#  A `TypeVar` rather than the 3.12 syntax because `requires-python` is `>=3.8`.
HandlerType = TypeVar("HandlerType", bound=Callable)
