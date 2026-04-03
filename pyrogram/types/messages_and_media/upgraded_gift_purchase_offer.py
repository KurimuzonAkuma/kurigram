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

from datetime import datetime
from typing import Dict, Optional

import pyrogram
from pyrogram import enums, raw, types, utils

from ..object import Object


class UpgradedGiftPurchaseOffer(Object):
    """An offer to purchase an upgraded gift was sent or received.

    Parameters:
        gift (:obj:`~pyrogram.types.Gift`):
            The gift.

        state (:obj:`~pyrogram.enums.GiftPurchaseOfferState`):
            State of the offer.

        price (:obj:`~pyrogram.types.GiftResalePrice`):
            The proposed price.

        expiration_date (:py:obj:`~datetime.datetime`):
            Date when the offer will expire or has expired.
    """

    def __init__(
        self,
        *,
        gift: "types.Gift",
        state: "enums.GiftPurchaseOfferState",
        price: "types.GiftResalePrice",
        expiration_date: datetime,
    ):
        super().__init__()

        self.gift = gift
        self.state = state
        self.price = price
        self.expiration_date = expiration_date

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        action: "raw.types.MessageActionStarGiftPurchaseOffer",
        users: Dict[int, "raw.base.User"] = {},
        chats: Dict[int, "raw.base.Chat"] = {},
    ) -> "UpgradedGiftPurchaseOffer":
        price = None

        if isinstance(action.price, raw.types.StarsTonAmount):
            price = types.GiftResalePriceTon(toncoin_cent_count=action.price.amount)
        elif isinstance(action.price, raw.types.StarsAmount):
            price = types.GiftResalePriceStar(star_count=action.price.amount)

        return UpgradedGiftPurchaseOffer(
            gift=await types.Gift._parse(client, action.gift, users=users, chats=chats),
            state=enums.GiftPurchaseOfferState.ACCEPTED
            if action.accepted
            else enums.GiftPurchaseOfferState.REJECTED
            if action.declined
            else enums.GiftPurchaseOfferState.PENDING,
            price=price,
            expiration_date=utils.timestamp_to_datetime(action.expires_at),
        )


class UpgradedGiftPurchaseOfferRejected(Object):
    """An offer to purchase a gift was rejected or expired.

    Parameters:
        gift (:obj:`~pyrogram.types.Gift`):
            The gift.

        price (:obj:`~pyrogram.types.GiftResalePrice`):
            The proposed price.

        offer_message_id (``int``):
            Identifier of the message with purchase offer which was rejected or expired.

        was_expired (``bool``):
            True, if the offer has expired; otherwise, the offer was explicitly rejected.
    """

    def __init__(
        self,
        *,
        gift: "types.Gift",
        price: "types.GiftResalePrice",
        offer_message_id: int,
        was_expired: bool,
    ):
        super().__init__()

        self.gift = gift
        self.price = price
        self.offer_message_id = offer_message_id
        self.was_expired = was_expired

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        action: "raw.types.MessageActionStarGiftPurchaseOfferDeclined",
        offer_message_id: Optional[int] = None,
        users: Dict[int, "raw.base.User"] = {},
        chats: Dict[int, "raw.base.Chat"] = {},
    ) -> "UpgradedGiftPurchaseOfferRejected":
        price = None

        if isinstance(action.price, raw.types.StarsTonAmount):
            price = types.GiftResalePriceTon(toncoin_cent_count=action.price.amount)
        elif isinstance(action.price, raw.types.StarsAmount):
            price = types.GiftResalePriceStar(star_count=action.price.amount)

        return UpgradedGiftPurchaseOfferRejected(
            gift=await types.Gift._parse(client, action.gift, users=users, chats=chats),
            price=price,
            offer_message_id=offer_message_id,
            was_expired=bool(action.expired),
        )
