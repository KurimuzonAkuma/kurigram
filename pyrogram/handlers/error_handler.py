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

from typing import Callable, Optional, Sequence, Union

import pyrogram
from pyrogram.filters import Filter
from pyrogram.types import Update

from .handler import Handler


class ErrorHandler(Handler):
    """The Error handler class. Used to handle unexpected errors.

    It is intended to be used with :meth:`~pyrogram.Client.add_handler`.

    For a more convenient way to register this handler, see the
    :meth:`~pyrogram.Client.on_error` decorator.

    Parameters:
        callback (``Callable``):
            A function that will be called whenever an unexpected error is raised.
            It takes the following positional arguments: *(exception, handler, client, *args)*.

        exceptions (``Exception`` | List of ``Exception``, *optional*):
            An exception type or a sequence of exception types that this handler should handle.
            If None, the handler will catch any exception that is a subclass of ``Exception``.

        filters (:obj:`Filter`, *optional*):
            Pass one or more filters to allow only a subset of updates to be passed
            in your callback function.

    Other parameters passed to the callback:
        client (:obj:`~pyrogram.Client`):
            The Client instance, useful when calling other API methods inside the error handler.

        exception (``Exception``):
            The Exception instance that was raised.

        handler (:obj:`~pyrogram.handlers.handler.Handler`):
            The Handler instance from which the exception was raised.

        update (:obj:`~pyrogram.raw.base.Update`):
            The received update, which can be one of the many single Updates listed in the
            :obj:`~pyrogram.raw.base.Update` base type.

        users (``dict``):
            Dictionary of all :obj:`~pyrogram.raw.base.User` mentioned in the update.
            You can access extra info about the user (such as *first_name*, *last_name*, etc...) by using
            the IDs you find in the *update* argument (e.g.: *users[1768841572]*).

        chats (``dict``):
            Dictionary of all :obj:`~pyrogram.raw.base.Chat` mentioned in the update.
            You can access extra info about the chat (such as *title*, *participants_count*, etc...)
            by using the IDs you find in the *update* argument (e.g.: *chats[1701277281]*).

    """

    def __init__(
        self,
        callback: Callable,
        exceptions: Optional[Union[Exception, Sequence[Exception]]] = None,
        filters: Optional[Filter] = None,
    ):
        super().__init__(callback, filters)

        if exceptions is None:
            self.exceptions = (Exception,)
        elif isinstance(exceptions, Sequence):
            self.exceptions = tuple(exceptions)
        else:
            self.exceptions = (exceptions,)
