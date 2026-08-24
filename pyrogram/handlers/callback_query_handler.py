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

from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, Any, Callable, Tuple

import pyrogram
from pyrogram.types import Identifier, ListenerTypes
from .handler import Handler

if TYPE_CHECKING:
    from pyrogram import types


class CallbackQueryHandler(Handler):
    """The CallbackQuery handler class. Used to handle callback queries coming from inline buttons.
    It is intended to be used with :meth:`~pyrogram.Client.add_handler`

    For a nicer way to register this handler, have a look at the
    :meth:`~pyrogram.Client.on_callback_query` decorator.

    Parameters:
        callback (``Callable``):
            Pass a function that will be called when a new CallbackQuery arrives. It takes *(client, callback_query)*
            as positional arguments (look at the section below for a detailed description).

        filters (:obj:`Filters`):
            Pass one or more filters to allow only a subset of callback queries to be passed
            in your callback function.

    Other parameters:
        client (:obj:`~pyrogram.Client`):
            The Client itself, useful when you want to call other API methods inside the message handler.

        callback_query (:obj:`~pyrogram.types.CallbackQuery`):
            The received callback query.
    """

    def __init__(
        self, callback: Callable[["pyrogram.Client", "types.CallbackQuery"], Any], filters=None
    ):
        self.original_callback = callback
        super().__init__(self.resolve_future_or_callback, filters)

    def compose_data_identifier(self, query: "types.CallbackQuery") -> Identifier:
        from_user = getattr(query, "from_user", None)
        from_user_id = from_user.id if from_user else None
        from_user_username = from_user.username if from_user else None

        chat_id = None
        message_id = None

        if getattr(query, "message", None):
            message_id = getattr(
                query.message, "id", getattr(query.message, "message_id", None)
            )

            if getattr(query.message, "chat", None):
                chat_id = [query.message.chat.id, query.message.chat.username]

        return Identifier(
            message_id=message_id,
            chat_id=chat_id,
            from_user_id=[from_user_id, from_user_username],
            inline_message_id=getattr(query, "inline_message_id", None),
        )

    async def check_if_has_matching_listener(
        self, client: "pyrogram.Client", query: "types.CallbackQuery"
    ) -> Tuple[bool, Any]:
        data = self.compose_data_identifier(query)

        listener = client.get_listener_matching_with_data(
            data, ListenerTypes.CALLBACK_QUERY
        )

        listener_does_match = False

        if listener:
            filters = listener.filters
            if callable(filters):
                if iscoroutinefunction(filters.__call__):
                    listener_does_match = await filters(client, query)
                else:
                    listener_does_match = await client.loop.run_in_executor(
                        None, filters, client, query
                    )
            else:
                listener_does_match = True

        return listener_does_match, listener

    async def check(self, client: "pyrogram.Client", query: "types.CallbackQuery") -> bool:
        listener_does_match, listener = await self.check_if_has_matching_listener(
            client, query
        )

        if callable(self.filters):
            if iscoroutinefunction(self.filters.__call__):
                handler_does_match = await self.filters(client, query)
            else:
                handler_does_match = await client.loop.run_in_executor(
                    None, self.filters, client, query
                )
        else:
            handler_does_match = True

        data = self.compose_data_identifier(query)

        if listener and not listener_does_match and listener.unallowed_click_alert:
            alert = (
                listener.unallowed_click_alert
                if isinstance(listener.unallowed_click_alert, str)
                else True
            )
            if alert is True:
                alert = "You are not allowed to click this button."
            if isinstance(alert, str):
                await query.answer(alert, show_alert=True)
            return False

        return listener_does_match or handler_does_match

    async def resolve_future_or_callback(
        self, client: "pyrogram.Client", query: "types.CallbackQuery", *args
    ):
        listener_does_match, listener = await self.check_if_has_matching_listener(
            client, query
        )

        if listener and listener_does_match:
            client.remove_listener(listener)

            if listener.future and not listener.future.done():
                listener.future.set_result(query)
                raise pyrogram.StopPropagation
            elif listener.callback:
                if iscoroutinefunction(listener.callback):
                    await listener.callback(client, query, *args)
                else:
                    listener.callback(client, query, *args)
                raise pyrogram.StopPropagation
            else:
                raise ValueError("Listener must have either a future or a callback")
        else:
            await self.original_callback(client, query, *args)
