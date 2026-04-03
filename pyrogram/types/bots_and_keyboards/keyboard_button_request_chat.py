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

from pyrogram import types

from ..object import Object


class KeyboardButtonRequestChat(Object):
    """Contains information about a chat peer type.

    Parameters:
        button_id (``int``):
            Identifier of button.

        chat_is_channel (``bool``):
            Pass True to request a channel chat, pass False to request a group or a supergroup chat.

        chat_is_forum (``bool``, *optional*):
            Pass True to request a forum supergroup, pass False to request a non-forum chat.
            If not specified, no additional restrictions are applied.

        chat_has_username (``bool``, *optional*):
            Pass True to request a supergroup or a channel with a username, pass False to request a chat without a username.
            If not specified, no additional restrictions are applied.

        chat_is_created (``bool``, *optional*):
            Pass True to request a chat owned by the user.
            Otherwise, no additional restrictions are applied.

        bot_is_member (``bool``, *optional*):
            Pass True to request a chat with the bot as a member.
            Otherwise, no additional restrictions are applied.

        user_administrator_rights (:obj:`~pyrogram.types.ChatAdministratorRights`, *optional*):
            Privileged actions that an user administrator is able to take.

        bot_administrator_rights (:obj:`~pyrogram.types.ChatAdministratorRights`, *optional*):
            Privileged actions that an bot administrator is able to take.

        request_title (``bool``, *optional*):
            Pass True to request the chats' title
            If not specified, the title won't be requested.

        request_username (``bool``, *optional*):
            Pass True to request the chats' username
            If not specified, the username won't be requested.

        request_photo (``bool``, *optional*):
            Pass True to request the chats' photo
            If not specified, the photo won't be requested.
    """

    def __init__(
        self, *,
        button_id: int,
        chat_is_channel: bool,
        chat_is_forum: bool = None,
        chat_has_username: bool = None,
        chat_is_created: bool = None,
        bot_is_member: bool = None,
        user_administrator_rights: "types.ChatAdministratorRights" = None,
        bot_administrator_rights: "types.ChatAdministratorRights" = None,
        request_title: bool = None,
        request_username: bool = None,
        request_photo: bool = None,
        max_quantity: int = 1,  # Telegram ignores this field for chats
    ):
        super().__init__()

        self.button_id = button_id
        self.chat_is_channel = chat_is_channel
        self.chat_is_created = chat_is_created
        self.bot_is_member = bot_is_member
        self.chat_has_username = chat_has_username
        self.chat_is_forum = chat_is_forum
        self.user_administrator_rights = user_administrator_rights
        self.bot_administrator_rights = bot_administrator_rights
        self.request_title = request_title
        self.request_username = request_username
        self.request_photo = request_photo
        self.max_quantity = max_quantity
