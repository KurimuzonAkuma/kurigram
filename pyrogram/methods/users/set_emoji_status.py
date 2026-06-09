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
from pyrogram import raw, types


class SetEmojiStatus:
    async def set_emoji_status(
        self: "pyrogram.Client",
        chat_id: Optional[Union[int, str]] = None,
        emoji_status: Optional["types.EmojiStatus"] = None
    ) -> bool:
        """Set the emoji status.

        .. note::

            For Telegram Premium users only.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                Defaults to the current user.

            emoji_status (:obj:`~pyrogram.types.EmojiStatus`, *optional*):
                New emoji status.
                Pass None to remove.

        Returns:
            ``bool``: On success, True is returned.

        Example:
            .. code-block:: python

                from pyrogram import types

                # Set emoji status of the current user
                await app.set_emoji_status(emoji_status=types.EmojiStatus(custom_emoji_id="1234567890987654321"))

                # Set collectible emoji status for a channel
                await app.set_emoji_status(
                    chat_id="channel_username",
                    emoji_status=types.EmojiStatus(gift_id=1234567890987654321)
                )
        """
        if chat_id is None:
            peer = raw.types.InputPeerSelf()
        else:
            peer = await self.resolve_peer(chat_id)

        if isinstance(peer, raw.types.InputPeerChannel):
            await self.invoke(
                raw.functions.channels.UpdateEmojiStatus(
                    channel=peer,
                    emoji_status=(
                        emoji_status.write()
                        if emoji_status
                        else raw.types.EmojiStatusEmpty()
                    )
                )
            )
        else:
            await self.invoke(
                raw.functions.account.UpdateEmojiStatus(
                    emoji_status=(
                        emoji_status.write()
                        if emoji_status
                        else raw.types.EmojiStatusEmpty()
                    )
                )
            )

        return True
