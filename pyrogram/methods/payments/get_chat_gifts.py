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

from typing import Optional, Union, AsyncGenerator

import pyrogram
from pyrogram import raw, types, utils


class GetChatGifts:
    async def get_chat_gifts(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        collection_id: Optional[int] = None,
        exclude_unsaved: Optional[bool] = None,
        exclude_saved: Optional[bool] = None,
        exclude_unlimited: Optional[bool] = None,
        exclude_upgradable: Optional[bool] = None,
        exclude_non_upgradable: Optional[bool] = None,
        exclude_upgraded: Optional[bool] = None,
        exclude_without_colors: Optional[bool] = None,
        exclude_hosted: Optional[bool] = None,
        sort_by_price: Optional[bool] = None,
        limit: int = 0,
        offset: str = ""
    ) -> AsyncGenerator["types.Gift", None]:
        """Get all gifts owned by specified chat.

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.
                For your personal cloud (Saved Messages) you can simply use "me" or "self".
                For a contact that exists in your Telegram address book you can use his phone number (str).

            collection_id (``int``, *optional*):
                Pass collection identifier to get gifts only from the specified collection.

            exclude_unsaved (``bool``, *optional*):
                Pass True to exclude gifts that aren’t saved to the account’s profile page.

            exclude_saved (``bool``, *optional*):
                Pass True to exclude gifts that are saved to the account’s profile page.

            exclude_unlimited (``bool``, *optional*):
                Pass True to exclude gifts that can be purchased an unlimited number of times.

            exclude_upgradable (``bool``, *optional*):
                Pass true to exclude gifts that can be purchased limited number of times and can be upgraded.

            exclude_non_upgradable (``bool``, *optional*):
                Pass true to exclude gifts that can be purchased limited number of times and can't be upgraded.

            exclude_upgraded (``bool``, *optional*):
                Pass True to exclude upgraded gifts.

            exclude_without_colors (``bool``, *optional*):
                Pass True to exclude gifts that can't be used in :meth:`~pyrogram.Client.set_upgraded_gift_colors`.

            exclude_hosted (``bool``, *optional*):
                Pass True to exclude gifts that are just hosted and are not owned by the owner.

            sort_by_price (``bool``, *optional*):
                Pass True to sort results by gift price instead of send date. Sorting is applied before pagination.

            offset (``str``, *optional*):
                Offset of the first entry to return as received from the previous request.

            limit (``int``, *optional*):
                The maximum number of gifts to be returned.

        Returns:
            ``Generator``: A generator yielding :obj:`~pyrogram.types.Gift` objects.

        Example:
            .. code-block:: python

                async for gift in app.get_chat_gifts(chat_id):
                    print(gift)
        """
        peer = await self.resolve_peer(chat_id)
        raw_peer_id = utils.get_raw_peer_id(peer)

        current = 0
        total = abs(limit) or (1 << 31) - 1
        limit = min(100, total)

        while True:
            r = await self.invoke(
                raw.functions.payments.GetSavedStarGifts(
                    peer=peer,
                    offset=offset,
                    limit=limit,
                    exclude_unsaved=exclude_unsaved,
                    exclude_saved=exclude_saved,
                    exclude_unlimited=exclude_unlimited,
                    exclude_unique=exclude_upgraded,
                    exclude_upgradable=exclude_upgradable,
                    exclude_unupgradable=exclude_non_upgradable,
                    peer_color_available=not exclude_without_colors if exclude_without_colors is not None else None,
                    exclude_hosted=exclude_hosted,
                    sort_by_value=sort_by_price,
                    collection_id=collection_id
                ),
                sleep_threshold=60
            )

            users = {i.id: i for i in r.users}
            chats = {i.id: i for i in r.chats}

            receiver = users.get(raw_peer_id) or chats.get(raw_peer_id)

            user_star_gifts = [
                await types.Gift._parse(self, gift, receiver, users=users, chats=chats)
                for gift in r.gifts
            ]

            if not user_star_gifts:
                return

            for gift in user_star_gifts:
                yield gift

                current += 1

                if current >= total:
                    return

            offset = r.next_offset

            if not offset:
                return

    get_received_gifts = get_chat_gifts
