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

from typing import TYPE_CHECKING, Any, Callable, List

from pyrogram.filters import Filter

from .handler import Handler

if TYPE_CHECKING:
    import pyrogram
    from pyrogram import types


class DeletedEphemeralMessagesHandler(Handler):
    """The deleted ephemeral messages handler class. Used to handle ephemeral messages that got
    deleted from any chat. It is intended to be used with :meth:`~pyrogram.Client.add_handler`

    For a nicer way to register this handler, have a look at the
    :meth:`~pyrogram.Client.on_deleted_ephemeral_messages` decorator.

    Parameters:
        callback (``Callable``):
            Pass a function that will be called when one or more ephemeral messages have been
            deleted. It takes *(client, messages)* as positional arguments (look at the section
            below for a detailed description).

        filters (:obj:`Filters`):
            Pass one or more filters to allow only a subset of messages to be passed
            in your callback function.

    Other parameters:
        client (:obj:`~pyrogram.Client`):
            The Client itself, useful when you want to call other API methods inside the handler.

        messages (List of :obj:`~pyrogram.types.EphemeralMessage`):
            The deleted ephemeral messages, as list.
    """

    def __init__(
        self,
        callback: Callable[["pyrogram.Client", List["types.EphemeralMessage"]], Any],
        filters: Filter = None,
    ):
        super().__init__(callback, filters)

    async def check(self, client: "pyrogram.Client", messages: List["types.EphemeralMessage"]):
        # Every message should be checked, if at least one matches the filter True is returned
        # otherwise, or if the list is empty, False is returned
        for message in messages:
            if await super().check(client, message):
                return True
        else:
            return False
