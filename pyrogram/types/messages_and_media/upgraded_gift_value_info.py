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
from typing import Optional

from pyrogram import raw, utils

from ..object import Object


class UpgradedGiftValueInfo(Object):
    """Contains information about value of an upgraded gift.

    Parameters:
        currency (``str``):
            ISO 4217 currency code of the currency in which the prices are represented.

        value (``int``):
            Estimated value of the gift; in the smallest units of the currency.

        is_value_average (``bool``):
            True, if the value is calculated as average value of similar sold gifts. Otherwise, it is based on the sale price of the gift.

        initial_sale_date (``int``):
            Point in time when the corresponding regular gift was originally purchased.

        initial_sale_star_count (``int``):
            Amount of Telegram Stars that were paid for the gift.

        initial_sale_price (``int``):
            Initial price of the gift; in the smallest units of the currency.

        last_sale_date (:py:obj:`~datetime.datetime`, *optional*):
            Point in time (Unix timestamp) when the upgraded gift was purchased last time.

        last_sale_price (``int``, *optional*):
            Last purchase price of the gift; in the smallest units of the currency.

        is_last_sale_on_fragment (``bool``, *optional*):
            True, if the last sale was completed on Fragment.

        minimum_price (``int``, *optional*):
            The current minimum price of gifts upgraded from the same gift.

        average_sale_price (``int``, *optional*):
            The average sale price in the last month of gifts upgraded from the same gift.

        telegram_listed_gift_count (``int``, *optional*):
            Number of gifts upgraded from the same gift being resold on Telegram.

        fragment_listed_gift_count (``int``, *optional*):
            Number of gifts upgraded from the same gift being resold on Fragment.

        fragment_url (``str``, *optional*):
            The HTTPS link to the Fragment for the gift.
    """
    def __init__(
        self, *,
        currency: str,
        value: int,
        is_value_average: bool,
        initial_sale_date: datetime,
        initial_sale_star_count: int,
        initial_sale_price: int,
        last_sale_date: Optional[datetime] = None,
        last_sale_price: Optional[int] = None,
        is_last_sale_on_fragment: Optional[bool] = None,
        minimum_price: Optional[int] = None,
        average_sale_price: Optional[int] = None,
        telegram_listed_gift_count: Optional[int] = None,
        fragment_listed_gift_count: Optional[int] = None,
        fragment_url: Optional[str] = None
    ):
        super().__init__()

        self.currency = currency
        self.value = value
        self.is_value_average = is_value_average
        self.initial_sale_date = initial_sale_date
        self.initial_sale_star_count = initial_sale_star_count
        self.initial_sale_price = initial_sale_price
        self.last_sale_date = last_sale_date
        self.last_sale_price = last_sale_price
        self.is_last_sale_on_fragment = is_last_sale_on_fragment
        self.minimum_price = minimum_price
        self.average_sale_price = average_sale_price
        self.telegram_listed_gift_count = telegram_listed_gift_count
        self.fragment_listed_gift_count = fragment_listed_gift_count
        self.fragment_url = fragment_url

    @staticmethod
    def _parse(value_info: "raw.types.payments.UniqueStarGiftValueInfo") -> "UpgradedGiftValueInfo":
        return UpgradedGiftValueInfo(
            currency=value_info.currency,
            value=value_info.value,
            is_value_average=value_info.value_is_average,
            initial_sale_date=utils.timestamp_to_datetime(value_info.initial_sale_date),
            initial_sale_star_count=value_info.initial_sale_stars,
            initial_sale_price=value_info.initial_sale_price,
            last_sale_date=utils.timestamp_to_datetime(value_info.last_sale_date),
            last_sale_price=value_info.last_sale_price,
            is_last_sale_on_fragment=value_info.last_sale_on_fragment,
            minimum_price=value_info.floor_price,
            average_sale_price=value_info.average_price,
            telegram_listed_gift_count=value_info.listed_count,
            fragment_listed_gift_count=value_info.fragment_listed_count,
            fragment_url=value_info.fragment_listed_url
        )
