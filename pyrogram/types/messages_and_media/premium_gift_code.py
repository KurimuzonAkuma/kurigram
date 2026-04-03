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

from pyrogram import raw, types, utils
from ..object import Object


class PremiumGiftCode(Object):
    """A Telegram Premium gift code was created for the user.

    Parameters:
        creator (:obj:`~pyrogram.types.Chat`, *optional*):
            Identifier of a chat or a user that created the gift code.

        text (:obj:`~pyrogram.types.FormattedText`, *optional*):
            Message added to the gift.

        is_from_giveaway (``bool``, *optional*):
            True, if the gift code was created for a giveaway.

        is_unclaimed (``bool``, *optional*):
            True, if the winner for the corresponding Telegram Premium subscription wasn't chosen.

        currency (``str``, *optional*):
            Currency for the paid amount.

        amount (``int``, *optional*):
            The paid amount, in the smallest units of the currency.

        cryptocurrency (``str``, *optional*):
            Cryptocurrency used to pay for the gift.

        cryptocurrency_amount (``int``, *optional*):
            The paid amount, in the smallest units of the cryptocurrency.

        month_count (``int``):
            Number of months the Telegram Premium subscription will be active after code activation.

        day_count (``int``):
            Number of days the Telegram Premium subscription will be active after code activation.

        sticker (:obj:`~pyrogram.types.Sticker`, *optional*):
            A sticker to be shown in the message.

        code (``str``):
            The gift code.

        link (``str``, *property*):
            Generate a link to this gift code.
    """

    def __init__(
        self,
        *,
        creator: Optional["types.Chat"] = None,
        text: Optional["types.FormattedText"] = None,
        is_from_giveaway: Optional[bool] = None,
        is_unclaimed: Optional[bool] = None,
        currency: Optional[str] = None,
        amount: Optional[int] = None,
        cryptocurrency: Optional[str] = None,
        cryptocurrency_amount: Optional[int] = None,
        month_count: int,
        day_count: int,
        sticker: Optional["types.Sticker"] = None,
        code: str
    ):
        super().__init__()

        self.creator = creator
        self.text = text
        self.is_from_giveaway = is_from_giveaway
        self.is_unclaimed = is_unclaimed
        self.currency = currency
        self.amount = amount
        self.cryptocurrency = cryptocurrency
        self.cryptocurrency_amount = cryptocurrency_amount
        self.month_count = month_count
        self.day_count = day_count
        self.sticker = sticker
        self.code = code

    @staticmethod
    async def _parse(client, giftcode: "raw.types.MessageActionGiftCode", users, chats):
        raw_peer_id = utils.get_raw_peer_id(giftcode.boost_peer)

        raw_stickers = await client.invoke(
            raw.functions.messages.GetStickerSet(
                stickerset=raw.types.InputStickerSetPremiumGifts(),
                hash=0
            )
        )

        return PremiumGiftCode(
            creator=types.Chat._parse_chat(client, users.get(raw_peer_id) or chats.get(raw_peer_id)),
            text=types.FormattedText._parse(client, giftcode.message),
            is_from_giveaway=giftcode.via_giveaway,
            is_unclaimed=giftcode.unclaimed,
            currency=giftcode.currency,
            amount=giftcode.amount,
            cryptocurrency=giftcode.crypto_currency,
            cryptocurrency_amount=giftcode.crypto_amount,
            month_count=utils.get_premium_duration_month_count(giftcode.days),
            day_count=giftcode.days,
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
            ),
            code=giftcode.slug
        )

    @property
    def link(self) -> str:
        return f"https://t.me/giftcode/{self.code}"
