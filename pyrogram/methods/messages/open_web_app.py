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

from typing import Optional, Union

import pyrogram
from pyrogram import enums, raw, types, utils


class OpenWebApp:
    async def open_web_app(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        bot_user_id: Union[int, str],
        url: Optional[str] = None,
        message_thread_id: Optional[int] = None,
        direct_messages_topic_id: Optional[int] = None,
        reply_parameters: Optional["types.ReplyParameters"] = None,
        platform: Optional["enums.ClientPlatform"] = None
    ) -> str:
        """Informs pyrogram that a Web App is being opened from the attachment menu,
        a :obj:`~pyrogram.types.MenuButton`, an url,
        or an :obj:`~pyrogram.types.InlineKeyboardButton` button.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            bot_user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

            url (``str``, *optional*):
                The URL from an :obj:`~pyrogram.types.InlineKeyboardButton` or a :obj:`~pyrogram.types.MenuButton`.

            message_thread_id (``int``, *optional*):
                If not None, the message thread identifier to which the message will be sent.

            direct_messages_topic_id (``int``, *optional*):
                If not None, unique identifier of the topic of channel direct messages chat to which the message will be sent.

            reply_parameters (:obj:`~pyrogram.types.ReplyParameters`, *optional*):
                Information about the message or story to be replied in the message sent by the Web App.

            platform (:obj:`~pyrogram.enums.ClientPlatform`, *optional*):
                The platform on which the link will be opened.

        Returns:
            ``str``: On success, returns the url of a Web App.

        Example:
            .. code-block:: python

                link = await app.open_web_app(chat_id, bot_user_id)
        """
        if platform is None:
            platform = self.client_platform

        r = await self.invoke(
            raw.functions.messages.RequestWebView(
                peer=await self.resolve_peer(chat_id),
                bot=await self.resolve_peer(bot_user_id),
                platform=platform.value,
                from_bot_menu=True if url is None else None,
                url=url,
                reply_to=await utils.get_reply_to(
                    client=self,
                    reply_parameters=reply_parameters,
                    message_thread_id=message_thread_id,
                    direct_messages_topic_id=direct_messages_topic_id
                ),

            )
        )

        return r.url
