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

from typing import List, Optional, Union

from pyrogram import enums, types

from ..object import Object


class ReplyParameters(Object):
    """Describes reply parameters for the message that is being sent.

    Parameters:
        message_id  (``int``, *optional*):
            Identifier of the message that will be replied to in the current chat, or in the chat chat_id if it is specified.

        story_id  (``int``, *optional*):
            Unique identifier for the story in the chat.

        chat_id (``int`` | ``str``, *optional*):
            If the message to be replied to is from a different chat.
            Unique identifier (int) or username (str) of the target chat.
            For your personal cloud (Saved Messages) you can simply use "me" or "self".
            For a contact that exists in your Telegram address book you can use his phone number (str).
            Not supported for messages sent on behalf of a business account and messages from channel direct messages chats.

        quote (``str``, *optional*):
            Quoted part of the message to be replied to, 0-1024 characters after entities parsing.
            The quote must be an exact substring of the message to be replied to, including bold, italic, underline, strikethrough, spoiler, and custom_emoji entities.
            The message will fail to send if the quote isn't found in the original message.

        quote_parse_mode (:obj:`~pyrogram.enums.ParseMode`, *optional*):
            By default, texts are parsed using both Markdown and HTML styles.
            You can combine both syntaxes together.

        quote_entities (List of :obj:`~pyrogram.types.MessageEntity`, *optional*):
            List of special entities that appear in message text, which can be specified instead of *quote_parse_mode*.

        quote_position (``int``, *optional*):
            Position of the quote in the original message in UTF-16 code units.

        checklist_task_id (``int``, *optional*):
            Identifier of the specific checklist task to be replied to.
    """

    def __init__(
        self,
        *,
        message_id: Optional[int] = None,
        story_id: Optional[int] = None,
        chat_id: Optional[Union[int, str]] = None,
        quote: Optional[str] = None,
        quote_parse_mode: Optional["enums.ParseMode"] = None,
        quote_entities: Optional[List["types.MessageEntity"]] = None,
        quote_position: Optional[int] = None,
        checklist_task_id: Optional[int] = None
    ):
        super().__init__()

        self.message_id = message_id
        self.story_id = story_id
        self.chat_id = chat_id
        self.quote = quote
        self.quote_parse_mode = quote_parse_mode
        self.quote_entities = quote_entities
        self.quote_position = quote_position
        self.checklist_task_id = checklist_task_id
