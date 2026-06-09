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

from typing import List, Optional, AsyncGenerator

import pyrogram
from pyrogram import enums, raw, types


class SearchGiftsForResale:
    async def search_gifts_for_resale(
        self: "pyrogram.Client",
        gift_id: int,
        order: "enums.GiftForResaleOrder" = enums.GiftForResaleOrder.CHANGE_DATE,
        for_crafting: Optional[bool] = None,
        for_stars: Optional[bool] = None,
        attributes: Optional[List["types.UpgradedGiftAttributeId"]] = None,
        limit: int = 0,
        offset: str = ""
    ) -> AsyncGenerator["types.Gift", None]:
        """Get upgraded gifts that can be bought from other owners.

        .. include:: /_includes/usable-by/users.rst

        Parameters:
            gift_id (``int``):
                Identifier of the regular gift that was upgraded to a unique gift.

            order (:obj:`~pyrogram.enums.GiftForResaleOrder`):
                Order in which the results will be sorted.

            for_crafting (``bool``, *optional*):
                Pass True to get only gifts suitable for crafting.

            for_stars (``bool``, *optional*):
                Pass True to get only gifts that can be bought using Telegram Stars.

            attributes (List of :obj:`~pyrogram.types.UpgradedGiftAttributeId`, *optional*):
                Attributes used to filter received gifts.
                If multiple attributes of the same type are specified, then all of them are allowed.
                If none attributes of specific type are specified, then all values for this attribute type are allowed.

            limit (``int``, *optional*):
                The maximum number of gifts to return. Default is 0 (no limit).

            offset (``str``, *optional*):
                The offset from which to start returning results. Default is "" (no offset).

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Gift` objects.

        Example:
            .. code-block:: python

                async for gift in app.search_gifts_for_resale(gift_id=123456):
                    print(gift)

                # Buy first gift from resale market
                async for gift in app.search_gifts_for_resale(gift_id=123456, limit=1):
                    await app.send_resold_gift(gift_link=gift.link, new_owner_chat_id="me") # or just use await gift.buy()
        """
        current = 0
        total = abs(limit) or (1 << 31) - 1
        limit = min(100, total)

        while True:
            r = await self.invoke(
                raw.functions.payments.GetResaleStarGifts(
                    gift_id=gift_id,
                    offset=offset,
                    limit=limit,
                    sort_by_price=order == enums.GiftForResaleOrder.PRICE,
                    sort_by_num=order == enums.GiftForResaleOrder.NUMBER,
                    for_craft=for_crafting,
                    stars_only=for_stars,
                    attributes=[attr.write() for attr in attributes] if attributes else None,

                ),
                sleep_threshold=60
            )

            users = {i.id: i for i in r.users}
            chats = {i.id: i for i in r.chats}

            gifts = [
                await types.Gift._parse(self, gift, users=users, chats=chats)
                for gift in r.gifts
            ]

            if not gifts:
                return

            for gift in gifts:
                yield gift

                current += 1

                if current >= total:
                    return

            offset = r.next_offset

            if not offset:
                return
