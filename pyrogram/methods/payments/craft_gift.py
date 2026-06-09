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

from typing import List

import pyrogram
from pyrogram import raw, types
from pyrogram import utils


class CraftGift:
    async def craft_gift(
        self: "pyrogram.Client",
        owned_gift_ids: List[str]
    ) -> "types.CraftGiftResult":
        """Crafts a new gift from other gifts that will be permanently lost.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            owned_gift_ids (List of ``str``):
                Identifier of the gifts to use for crafting.

        Returns:
            :obj:`~pyrogram.types.CraftGiftResult`: On success, returns the result of gift crafting.
        """
        r = await self.invoke(
            raw.functions.payments.CraftStarGift(
                stargift=[await utils.get_input_stargift(self, owned_gift_id) for owned_gift_id in owned_gift_ids],
            )
        )

        users = {i.id: i for i in r.users}
        chats = {i.id: i for i in r.chats}

        for u in r.updates:
            if isinstance(u, raw.types.UpdateStarGiftCraftFail):
                return types.CraftGiftResultFail()

            elif isinstance(u, raw.types.UpdateNewMessage):
                message = await types.Message._parse(
                    self,
                    u.message,
                    users,
                    chats,
                    business_connection_id=getattr(u, "connection_id", None),
                    raw_reply_to_message=getattr(u, "reply_to_message", None)
                )

                return types.CraftGiftResultSuccess(
                    gift=message.gift
                )
