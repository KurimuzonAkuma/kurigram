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


class GetWebAppUrl:
    async def get_web_app_url(
        self: "pyrogram.Client",
        bot_user_id: Union[int, str],
        url: Optional[str] = None,
        platform: Optional["enums.ClientPlatform"] = None
    ) -> str:
        """Returns an HTTPS URL of a Web App to open from the side menu,
        a :obj:`~pyrogram.types.KeyboardButton` button with web app type,
        or an :obj:`~pyrogram.types.InlineKeyboardButton` button with web app type.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            bot_user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target bot.

            url (``str``, *optional*):
                The URL from :obj:`~pyrogram.types.KeyboardButton` button with web app type,
                or an :obj:`~pyrogram.types.InlineKeyboardButton` button with web app type,
                or an None when the bot is opened from the side menu.

            platform (:obj:`~pyrogram.enums.ClientPlatform`, *optional*):
                The platform on which the link will be opened.

        Returns:
            ``str``: On success, returns the url of a Web App.

        Example:
            .. code-block:: python

                link = await client.get_web_app_url(bot_user_id)
        """
        if platform is None:
            platform = self.client_platform

        r = await self.invoke(
            raw.functions.messages.RequestSimpleWebView(
                bot=await self.resolve_peer(bot_user_id),
                platform=platform.value,
                from_side_menu=True if url is None else None,
                url=url
            )
        )

        return r.url
