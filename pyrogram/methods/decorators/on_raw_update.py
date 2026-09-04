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

from typing import Callable, Optional

import pyrogram
from pyrogram.filters import Filter
from .handler_type import HandlerType


class OnRawUpdate:
    def on_raw_update(
        self: Optional["OnRawUpdate"] = None,
        filters=None,
        group: int = 0,
    ) -> Callable[[HandlerType], HandlerType]:
        """Decorator for handling raw updates.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.RawUpdateHandler`.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of updates to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: HandlerType) -> HandlerType:
            if isinstance(self, pyrogram.Client):
                self.add_handler(pyrogram.handlers.RawUpdateHandler(func, filters), group)
            elif isinstance(self, Filter) or self is None:
                if not hasattr(func, "handlers"):
                    func.handlers = []

                func.handlers.append(
                    (
                        pyrogram.handlers.RawUpdateHandler(func, self),
                        group if filters is None else filters
                    )
                )

            return func

        return decorator
