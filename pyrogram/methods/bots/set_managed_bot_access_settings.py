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

import pyrogram
from pyrogram import raw


class SetManagedBotAccessSettings:
    async def set_managed_bot_access_settings(
        self: "pyrogram.Client",
        user_id: Union[int, str],
        is_access_restricted: bool,
        added_user_ids: Optional[List[Union[int, str]]] = None,
    ) -> bool:
        """Use this method to get the access settings of a managed bot.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the managed bot whose access settings will be changed.

            is_access_restricted (``bool``):
                Pass True, if only selected users can access the bot.
                The bot's owner can always access it.

            added_user_ids (List of ``int`` | ``str``, *optional*):
                List of up to 10 identifiers of users who will have access to the bot in addition to its owner.
                Ignored if is_access_restricted is False.

        Returns:
            ``bool``: On success, True is returned.
        """
        if is_access_restricted is False:
            added_user_ids = None

        return await self.invoke(
            raw.functions.bots.EditAccessSettings(
                bot=await self.resolve_peer(user_id),
                restricted=is_access_restricted,
                add_users=[await self.resolve_peer(i) for i in added_user_ids] if added_user_ids is not None else None,
            )
        )
