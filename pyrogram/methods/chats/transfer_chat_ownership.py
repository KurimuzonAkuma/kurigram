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

from typing import Union

import pyrogram
from pyrogram import raw, utils


class TransferChatOwnership:
    async def transfer_chat_ownership(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        user_id: Union[int, str],
        password: str,
    ) -> bool:
        """Change the owner of a chat or channel.

        .. note::

            Requires owner privileges.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                Unique identifier for the target chat in form of a *t.me/joinchat/* link, identifier (int) or username
                of the target channel/supergroup (in the format @username).

            user_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the new owner.
                For a contact that exists in your Telegram address book you can use his phone number (str).

            password (``str``):
                The 2-step verification password of the current user.

        Returns:
            ``bool``: True on success.

        Raises:
            ValueError: In case of invalid parameters.
            RPCError: In case of a Telegram RPC error.

        Example:
            .. code-block:: python

                await app.transfer_chat_ownership(chat_id, user_id, "password")
        """
        peer_channel = await self.resolve_peer(chat_id)
        peer_user = await self.resolve_peer(user_id)

        if not isinstance(peer_channel, raw.types.InputPeerChannel):
            raise ValueError("The chat_id must belong to a channel/supergroup.")

        if not isinstance(peer_user, raw.types.InputPeerUser):
            raise ValueError("The user_id must belong to a user.")

        r = await self.invoke(
            raw.functions.messages.EditChatCreator(
                peer=peer_channel,
                user_id=peer_user,
                password=utils.compute_password_check(
                    await self.invoke(raw.functions.account.GetPassword()), password
                ),
            )
        )

        return bool(r)
