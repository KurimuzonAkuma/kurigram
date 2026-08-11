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

import random
from typing import Optional

from pyrogram import raw, types

from ..object import Object


class GiftedStars(Object):
    """Telegram Stars were gifted to a user.

    Parameters:
        gifter (:obj:`~pyrogram.types.User`, *optional*):
            User that gifted Telegram Premium.
            None if the gift was anonymous.

        receiver (:obj:`~pyrogram.types.User`):
            User that received Telegram Premium.

        currency (``str``):
            Currency for the paid amount.

        amount (``int``):
            The paid amount, in the smallest units of the currency.

        cryptocurrency (``str``, *optional*):
            Cryptocurrency used to pay for the gift.

        cryptocurrency_amount (``int``, *optional*):
            The paid amount, in the smallest units of the cryptocurrency.

        star_count (``int``):
            Number of Telegram Stars that were gifted.

        transaction_id (``str``, *optional*):
            Identifier of the transaction for Telegram Stars purchase.
            For receiver only.

        sticker (:obj:`~pyrogram.types.Sticker`):
            A sticker to be shown in the message.
    """
    def __init__(
        self,
        *,
        gifter: Optional["types.User"] = None,
        receiver: "types.User",
        currency: Optional[str] = None,
        amount: Optional[int] = None,
        cryptocurrency: Optional[str] = None,
        cryptocurrency_amount: Optional[int] = None,
        star_count: Optional[int] = None,
        transaction_id: Optional[str] = None,
        sticker: Optional["types.Sticker"] = None,
    ):
        super().__init__()

        self.gifter = gifter
        self.receiver = receiver
        self.currency = currency
        self.amount = amount
        self.cryptocurrency = cryptocurrency
        self.cryptocurrency_amount = cryptocurrency_amount
        self.star_count = star_count
        self.transaction_id = transaction_id
        self.sticker = sticker

    @staticmethod
    async def _parse(
        client,
        action: "raw.types.MessageActionGiftStars",
        gifter: Optional["raw.base.User"] = None,
        receiver: Optional["raw.base.User"] = None,
    ) -> "GiftedStars":
        raw_stickers = await client.invoke(
            raw.functions.messages.GetStickerSet(
                stickerset=raw.types.InputStickerSetPremiumGifts(),
                hash=0
            )
        )

        return GiftedStars(
            gifter=types.User._parse(client, gifter),
            receiver=types.User._parse(client, receiver),
            currency=action.currency,
            amount=action.amount,
            cryptocurrency=getattr(action, "crypto_currency", None),
            cryptocurrency_amount=getattr(action, "crypto_amount", None),
            star_count=action.stars,
            transaction_id=getattr(action, "transaction_id", None),
            sticker=random.choice(
                types.List(
                    [
                        await types.Sticker._parse(
                            client,
                            doc,
                            {
                                type(i): i for i in doc.attributes
                            }
                        ) for doc in raw_stickers.documents
                    ]
                )
            )
        )
