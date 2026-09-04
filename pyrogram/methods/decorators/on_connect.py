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
from .handler_type import HandlerType


class OnConnect:
    def on_connect(self: Optional["OnConnect"] = None) -> Callable[[HandlerType], HandlerType]:
        """Decorator for handling connections.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.ConnectHandler`.

        .. include:: /_includes/usable-by/users-bots.rst
        """

        def decorator(func: HandlerType) -> HandlerType:
            if isinstance(self, pyrogram.Client):
                self.add_handler(pyrogram.handlers.ConnectHandler(func))
            else:
                if not hasattr(func, "handlers"):
                    func.handlers = []

                func.handlers.append((pyrogram.handlers.ConnectHandler(func), 0))

            return func

        return decorator
