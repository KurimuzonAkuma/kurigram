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
from pyrogram import raw


class SetBotName:
    async def set_bot_name(
        self: "pyrogram.Client",
        name: str,
        language_code: str = "",
        for_my_bot: Optional[Union[int, str]] = None,
    ) -> str:
        """Use this method to get the current / owned bot name for the given user language.
        
        .. note::

            If the current account is an User, can be called only if the ``for_my_bot`` has ``can_be_edited`` property set to True.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            name (``str``):
                New bot name; 0-64 characters. Pass an empty string to remove the dedicated name for the given language.

            language_code (``str``, *optional*):
                A two-letter ISO 639-1 language code or an empty string

            for_my_bot (``int`` | ``str``, *optional*):
                Unique identifier (int) or username (str) of the bot for which profile photo has to be updated instead of the current user.
                The bot should have ``can_be_edited`` property set to True.

        Returns:
            ``bool``: True on success.

        Example:
            .. code-block:: python

                await app.set_bot_name("Pyrogram Assistant")
        """

        return await self.invoke(
            raw.functions.bots.SetBotInfo(
                bot=await self.resolve_peer(for_my_bot) if for_my_bot else None,
                lang_code=language_code,
                name=name
            )
        )
