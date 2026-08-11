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
from pyrogram import raw, enums


class GetWebAppLinkUrl:
    async def get_web_app_link_url(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        bot_user_id: Union[int, str],
        web_app_short_name: str,
        start_parameter: str = "",
        allow_write_access: bool = False,
        platform: Optional["enums.ClientPlatform"] = None
    ) -> str:
        """Returns an HTTPS URL of a Web App to open.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            bot_user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

            web_app_short_name (``str``):
                Short name of the Web App.

            start_parameter (``str``, *optional*):
                Start parameter.

            allow_write_access (``bool``, *optional*):
                Pass True if the current user allowed the bot to send them messages.

            platform (:obj:`~pyrogram.enums.ClientPlatform`, *optional*):
                The platform on which the link will be opened.

        Returns:
            ``str``: On success, returns the url of a Web App.

        Example:
            .. code-block:: python

                link = await app.get_web_app_link_url(chat_id, bot_user_id, web_app_short_name)
        """
        if platform is None:
            platform = self.client_platform

        r = await self.invoke(
            raw.functions.messages.RequestAppWebView(
                peer=await self.resolve_peer(chat_id),
                app=raw.types.InputBotAppShortName(
                    bot_id=await self.resolve_peer(bot_user_id),
                    short_name=web_app_short_name
                ),
                platform=platform.value,
                write_allowed=allow_write_access,
                start_param=start_parameter,

            )
        )

        return r.url
