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

import logging
from typing import List, Match, Optional, Union

import pyrogram
from pyrogram import raw, types

from ..object import Object
from ..update import Update

log = logging.getLogger(__name__)


class EphemeralCallbackQuery(Object, Update):
    """An incoming callback query from a callback button attached to an ephemeral message.

    Parameters:
        id (``str``):
            Unique identifier for this query.

        from_user (:obj:`~pyrogram.types.User`):
            Sender.

        message (:obj:`~pyrogram.types.EphemeralMessage`, *optional*):
            The ephemeral message with the callback button that originated the query.

        data (``str`` | ``bytes``, *optional*):
            Data associated with the callback button. Be aware that a bad client can send arbitrary
            data in this field.

        matches (List of regex Matches, *optional*):
            A list containing all `Match Objects <https://docs.python.org/3/library/re.html#match-objects>`_
            that match the data of this callback query. Only applicable when using
            :obj:`Filters.regex <pyrogram.Filters.regex>`.
    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        id: str,
        from_user: "types.User",
        message: "types.EphemeralMessage" = None,
        data: Union[str, bytes] = None,
        matches: List[Match] = None
    ):
        super().__init__(client)

        self.id = id
        self.from_user = from_user
        self.message = message
        self.data = data
        self.matches = matches

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        update: "raw.types.UpdateEphemeralBotCallbackQuery",
        users,
        chats,
    ) -> "EphemeralCallbackQuery":
        data = getattr(update, "data", None)

        if data:
            try:
                data = data.decode()
            except (UnicodeDecodeError, AttributeError):
                pass

        return EphemeralCallbackQuery(
            id=str(update.query_id),
            from_user=types.User._parse(client, users.get(update.user_id)),
            message=await types.EphemeralMessage._parse(client, update.message, users, chats),
            data=data,
            client=client,
        )

    async def answer(self, text: str = None, show_alert: bool = None, url: str = None, cache_time: int = 0):
        """Bound method *answer* of :obj:`~pyrogram.types.EphemeralCallbackQuery`.

        Use this method as a shortcut for:

        .. code-block:: python

            await client.answer_callback_query(
                ephemeral_callback_query.id,
                text="Hello",
                show_alert=True
            )

        Parameters:
            text (``str``, *optional*):
                Text of the notification. If not specified, nothing will be shown to the user.

            show_alert (``bool`` *optional*):
                If true, an alert will be shown by the client instead of a notification at the top of
                the chat screen.

            url (``str`` *optional*):
                URL that will be opened by the user's client.

            cache_time (``int`` *optional*):
                The maximum amount of time in seconds that the result of the callback query may be
                cached client-side.
        """
        return await self._client.answer_callback_query(
            callback_query_id=self.id,
            text=text,
            show_alert=show_alert,
            url=url,
            cache_time=cache_time
        )

    async def edit_message_text(
        self,
        text: str,
        entities: List["types.MessageEntity"] = None,
        reply_markup: "types.InlineKeyboardMarkup" = None,
    ) -> "types.EphemeralMessage":
        """Bound method *edit_message_text* of :obj:`~pyrogram.types.EphemeralCallbackQuery`.

        Use this method as a shortcut for:

        .. code-block:: python

            await client.edit_ephemeral_message_text(
                chat_id=ephemeral_callback_query.message.chat.id,
                receiver_id=ephemeral_callback_query.message.receiver.id,
                message_id=ephemeral_callback_query.message.id,
                text="new text"
            )

        Returns:
            :obj:`~pyrogram.types.EphemeralMessage`: On success, the edited message is returned.
        """
        return await self._client.edit_ephemeral_message_text(
            chat_id=self.message.chat.id,
            receiver_id=self.message.receiver.id,
            message_id=self.message.id,
            text=text,
            entities=entities,
            reply_markup=reply_markup,
        )
