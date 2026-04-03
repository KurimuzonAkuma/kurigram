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

from typing import List, Union

import pyrogram
from pyrogram import raw, types, utils


class RemoveCollectionGifts:
    async def remove_collection_gifts(
        self: "pyrogram.Client",
        owner_id: Union[int, str],
        collection_id: int,
        gift_ids: List[str]
    ) -> "types.GiftCollection":
        """Removes gifts from a collection.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            owner_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".

            collection_id (``int``):
                Identifier of the gift collection.

            gift_ids (List of ``str``):
                Identifier of the gifts to remove from the collection.

        Returns:
            :obj:`~pyrogram.types.GiftCollection`: On success, a updated collection is returned.

        Example:
            .. code-block:: python

                await app.remove_collection_gifts("me", 123, ["https://t.me/nft/NekoHelmet-9215"])
        """
        stargifts = []

        for gift in gift_ids:
            stargifts.append(await utils.get_input_stargift(self, gift))

        r = await self.invoke(
            raw.functions.payments.UpdateStarGiftCollection(
                peer=await self.resolve_peer(owner_id),
                collection_id=collection_id,
                delete_stargift=stargifts
            )
        )

        return await types.GiftCollection._parse(self, r)
