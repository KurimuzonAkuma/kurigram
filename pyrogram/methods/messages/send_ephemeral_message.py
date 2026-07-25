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
from typing import List, Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils

log = logging.getLogger(__name__)


class SendEphemeralMessage:
    async def send_ephemeral_message(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        receiver_id: Union[int, str],
        text: str = "",
        parse_mode: Optional["enums.ParseMode"] = None,
        entities: Optional[List["types.MessageEntity"]] = None,
        media: Optional["types.InputMedia"] = None,
        reply_to_message_id: Optional[int] = None,
        reply_markup: Optional[Union[
            "types.InlineKeyboardMarkup",
            "types.ReplyKeyboardMarkup",
            "types.ReplyKeyboardRemove",
            "types.ForceReply"
        ]] = None,
    ) -> "types.EphemeralMessage":
        """Send an ephemeral message.

        Ephemeral messages are lightweight messages that only the ``receiver_id`` user can see.
        They don't become part of the regular chat history and can't be forwarded or fetched later
        with :meth:`~pyrogram.Client.get_messages`.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            receiver_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the only user allowed to see this
                message.

            text (``str``, *optional*):
                Text of the message to be sent.

            parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
                By default, texts are parsed using both Markdown and HTML styles.
                You can combine both syntaxes together.

            entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
                List of special entities that appear in message text, which can be specified
                instead of *parse_mode*.

            media (:obj:`~pyrogram.types.InputMedia`, *optional*):
                Media to attach to the message.

            reply_to_message_id (``int``, *optional*):
                If the message is a reply, the id of the ephemeral message it replies to.

            reply_markup (:obj:`~pyrogram.types.InlineKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardMarkup` | :obj:`~pyrogram.types.ReplyKeyboardRemove` | :obj:`~pyrogram.types.ForceReply`, *optional*):
                Additional interface options. An object for an inline keyboard, custom reply keyboard,
                instructions to remove reply keyboard or to force a reply from the user.

        Returns:
            :obj:`~pyrogram.types.EphemeralMessage`: On success, the sent ephemeral message is returned.

        Example:
            .. code-block:: python

                await app.send_ephemeral_message(chat_id, receiver_id, "This message will vanish!")
        """
        message, entities = (await utils.parse_text_entities(self, text, parse_mode, entities)).values()

        r = await self.invoke(
            raw.functions.ephemeral.SendMessage(
                peer=await self.resolve_peer(chat_id),
                receiver_id=await utils.resolve_receiver(self, receiver_id),
                message=message,
                random_id=self.rnd_id(),
                entities=entities,
                media=await media.write(self) if media else None,
                reply_markup=await reply_markup.write(self) if reply_markup else None,
                reply_to=(
                    raw.types.InputReplyToEphemeralMessage(id=reply_to_message_id)
                    if reply_to_message_id
                    else None
                ),
            )
        )

        return await utils.parse_ephemeral_message(self, r)
