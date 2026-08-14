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
from pyrogram import enums, raw, types
from pyrogram.errors import ChannelPrivate

from ... import utils
from ..object import Object
from ..update import Update

log = logging.getLogger(__name__)

class CallbackQuery(Object, Update):
    """An incoming callback query from a callback button in an inline keyboard.

    If the button that originated the query was attached to a message sent by the bot, the field *message*
    will be present. If the button was attached to a message sent via the bot (in inline mode), the field
    *inline_message_id* will be present. Exactly one of the fields *data* or *game_short_name* will be present.

    Parameters:
        id (``str``):
            Unique identifier for this query.

        from_user (:obj:`~pyrogram.types.User`):
            Sender.

        chat_instance (``str``, *optional*):
            Global identifier, uniquely corresponding to the chat to which the message with the callback button was
            sent. Useful for high scores in games.

        message (:obj:`~pyrogram.types.Message`, *optional*):
            Message with the callback button that originated the query. Note that message content and message date will
            not be available if the message is too old.

        inline_message_id (``str``):
            Identifier of the message sent via the bot in inline mode, that originated the query.

        data (``str`` | ``bytes``, *optional*):
            Data associated with the callback button. Be aware that a bad client can send arbitrary data in this field.

        game_short_name (``str``, *optional*):
            Short name of a Game to be returned, serves as the unique identifier for the game.

        matches (List of regex Matches, *optional*):
            A list containing all `Match Objects <https://docs.python.org/3/library/re.html#match-objects>`_ that match
            the data of this callback query. Only applicable when using :obj:`Filters.regex <pyrogram.Filters.regex>`.

        chat (:obj:`~pyrogram.types.Chat`, *property*):
            The chat *message* was sent in. None for a button attached to an inline message, which carries
            *inline_message_id* instead.
    """

    def __init__(
        self,
        *,
        client: Optional["pyrogram.Client"] = None,
        id: str,
        from_user: "types.User",
        chat_instance: Optional[str] = None,
        message: Optional["types.Message"] = None,
        inline_message_id: Optional[str] = None,
        data: Optional[Union[str, bytes]] = None,
        game_short_name: Optional[str] = None,
        matches: Optional[List[Match]] = None
    ):
        super().__init__(client)

        self.id = id
        self.from_user = from_user
        self.chat_instance = chat_instance
        self.message = message
        self.inline_message_id = inline_message_id
        self.data = data
        self.game_short_name = game_short_name
        self.matches = matches

    @property
    def chat(self) -> Optional["types.Chat"]:
        return self.message.chat if self.message else None

    @staticmethod
    async def _parse(client: "pyrogram.Client", callback_query, users, chats) -> "CallbackQuery":
        message = None
        inline_message_id = None

        if isinstance(callback_query, raw.types.UpdateBotCallbackQuery):
            chat_id = utils.get_peer_id(callback_query.peer)
            message_id = callback_query.msg_id

            message = client.message_cache[(chat_id, message_id)]

            if not message:
                try:
                    message = await client.get_messages(
                        chat_id=chat_id,
                        message_ids=message_id
                    )
                except ChannelPrivate:
                    channel = chats.get(utils.get_raw_peer_id(callback_query.peer), None)
                    if channel:
                        message = types.Message(
                            id=message_id,
                            chat=types.Chat._parse_chat(
                                client,
                                channel
                            )
                        )
        elif isinstance(callback_query, raw.types.UpdateInlineBotCallbackQuery):
            inline_message_id = utils.pack_inline_message_id(callback_query.msg_id)
        elif isinstance(callback_query, raw.types.UpdateBusinessBotCallbackQuery):
            message = await types.Message._parse(
                client,
                callback_query.message,
                users,
                chats,
                is_scheduled=False,
                replies=0,
                business_connection_id=callback_query.connection_id,
                raw_reply_to_message=getattr(callback_query, "reply_to_message", None)
            )
        elif isinstance(callback_query, raw.types.UpdateEphemeralBotCallbackQuery):
            message = await types.Message._parse(
                client,
                callback_query.message,
                users,
                chats,
                replies=0
            )

        # Try to decode callback query data into string. If that fails, fallback to bytes instead of decoding by
        # ignoring/replacing errors, this way, button clicks will still work.
        data = getattr(callback_query, "data", None)

        if data:
            try:
                data = data.decode()
            except (UnicodeDecodeError, AttributeError):
                data = data

        return CallbackQuery(
            id=str(callback_query.query_id),
            from_user=types.User._parse(client, users[callback_query.user_id]),
            message=message,
            inline_message_id=inline_message_id,
            chat_instance=str(callback_query.chat_instance) if hasattr(callback_query, "chat_instance") else None,
            data=data,
            game_short_name=getattr(callback_query, "game_short_name", None),
            client=client
        )

    async def answer(self, text: Optional[str] = None, show_alert: Optional[bool] = None, url: Optional[str] = None, cache_time: int = 0):
        """Bound method *answer* of :obj:`~pyrogram.types.CallbackQuery`.

        Use this method as a shortcut for:

        .. code-block:: python

            await client.answer_callback_query(
                callback_query.id,
                text="Hello",
                show_alert=True
            )

        Example:
            .. code-block:: python

                await callback_query.answer("Hello", show_alert=True)

        Parameters:
            text (``str``, *optional*):
                Text of the notification. If not specified, nothing will be shown to the user, 0-200 characters.

            show_alert (``bool`` *optional*):
                If true, an alert will be shown by the client instead of a notification at the top of the chat screen.
                Defaults to False.

            url (``str`` *optional*):
                URL that will be opened by the user's client.
                If you have created a Game and accepted the conditions via @Botfather, specify the URL that opens your
                game – note that this will only work if the query comes from a callback_game button.
                Otherwise, you may use links like t.me/your_bot?start=XXXX that open your bot with a parameter.

            cache_time (``int`` *optional*):
                The maximum amount of time in seconds that the result of the callback query may be cached client-side.
                Telegram apps will support caching starting in version 3.14. Defaults to 0.
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
        text: Optional[str] = None,
        parse_mode: Optional["enums.ParseMode"] = None,
        link_preview_options: Optional["types.LinkPreviewOptions"] = None,
        rich_message: Optional["types.InputRichMessage"] = None,
        reply_markup: Optional["types.InlineKeyboardMarkup"] = None,
        disable_web_page_preview: Optional[bool] = None,
    ) -> Union["types.Message", bool]:
        """Edit the text of messages attached to callback queries.

        Bound method *edit_message_text* of :obj:`~pyrogram.types.CallbackQuery`.

        Parameters:
            text (``str``, *optional*):
                New text of the message.
                Required if rich_message isn't specified.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            link_preview_options (:obj:`~pyrogram.types.LinkPreviewOptions`, *optional*):
                Options used for link preview generation for the message.

            rich_message (:obj:`~pyrogram.types.InputRichMessage`, *optional*):
                New rich content of the message.
                Required if text isn't specified.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            :obj:`~pyrogram.types.Message` | ``bool``: On success, if the edited message was sent by the bot, the edited
            message is returned, otherwise True is returned (message sent via the bot, as inline query result).

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if disable_web_page_preview is not None:
            log.warning(
                "`disable_web_page_preview` is deprecated and will be removed in future updates. Use `link_preview_options` instead."
            )
            link_preview_options = types.LinkPreviewOptions(is_disabled=disable_web_page_preview)

        if self.inline_message_id is None:
            return await self._client.edit_message_text(
                chat_id=self.message.chat.id,
                message_id=self.message.id,
                text=text,
                parse_mode=parse_mode,
                link_preview_options=link_preview_options,
                rich_message=rich_message,
                reply_markup=reply_markup
            )
        else:
            return await self._client.edit_inline_text(
                inline_message_id=self.inline_message_id,
                text=text,
                parse_mode=parse_mode,
                link_preview_options=link_preview_options,
                rich_message=rich_message,
                reply_markup=reply_markup
            )

    async def edit_message_caption(
        self,
        caption: str,
        parse_mode: Optional["enums.ParseMode"] = None,
        reply_markup: Optional["types.InlineKeyboardMarkup"] = None
    ) -> Union["types.Message", bool]:
        """Edit the caption of media messages attached to callback queries.

        Bound method *edit_message_caption* of :obj:`~pyrogram.types.CallbackQuery`.

        Parameters:
            caption (``str``):
                New caption of the message.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            :obj:`~pyrogram.types.Message` | ``bool``: On success, if the edited message was sent by the bot, the edited
            message is returned, otherwise True is returned (message sent via the bot, as inline query result).

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        return await self.edit_message_text(caption, parse_mode, reply_markup=reply_markup)

    async def edit_message_media(
        self,
        media: "types.InputMedia",
        reply_markup: Optional["types.InlineKeyboardMarkup"] = None
    ) -> Union["types.Message", bool]:
        """Edit animation, audio, document, photo or video messages attached to callback queries.

        Bound method *edit_message_media* of :obj:`~pyrogram.types.CallbackQuery`.

        Parameters:
            media (:obj:`~pyrogram.types.InputMedia`):
                One of the InputMedia objects describing an animation, audio, document, photo or video.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`, *optional*):
                An InlineKeyboardMarkup object.

        Returns:
            :obj:`~pyrogram.types.Message` | ``bool``: On success, if the edited message was sent by the bot, the edited
            message is returned, otherwise True is returned (message sent via the bot, as inline query result).

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if self.inline_message_id is None:
            return await self._client.edit_message_media(
                chat_id=self.message.chat.id,
                message_id=self.message.id,
                media=media,
                reply_markup=reply_markup
            )
        else:
            return await self._client.edit_inline_media(
                inline_message_id=self.inline_message_id,
                media=media,
                reply_markup=reply_markup
            )

    async def edit_message_reply_markup(
        self,
        reply_markup: Optional["types.InlineKeyboardMarkup"] = None
    ) -> Union["types.Message", bool]:
        """Edit only the reply markup of messages attached to callback queries.

        Bound method *edit_message_reply_markup* of :obj:`~pyrogram.types.CallbackQuery`.

        Parameters:
            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup`):
                An InlineKeyboardMarkup object.

        Returns:
            :obj:`~pyrogram.types.Message` | ``bool``: On success, if the edited message was sent by the bot, the edited
            message is returned, otherwise True is returned (message sent via the bot, as inline query result).

        Raises:
            RPCError: In case of a Telegram RPC error.
        """
        if self.inline_message_id is None:
            return await self._client.edit_message_reply_markup(
                chat_id=self.message.chat.id,
                message_id=self.message.id,
                reply_markup=reply_markup
            )
        else:
            return await self._client.edit_inline_reply_markup(
                inline_message_id=self.inline_message_id,
                reply_markup=reply_markup
            )
