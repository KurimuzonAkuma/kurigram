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
from typing import List, Optional

from pyrogram import raw, types, utils

from ..object import Object


class AuctionState(Object):
    """Describes state of an auction.

    It can be one of:

    - :obj:`~pyrogram.types.AuctionStateActive`
    - :obj:`~pyrogram.types.AuctionStateFinished`
    """

    def __init__(self):
        super().__init__()


class AuctionStateActive(AuctionState):
    """Contains information about an ongoing auction.

    Parameters:
        start_date (:py:obj:`~datetime.datetime`):
            Date the action was started.

        end_date (:py:obj:`~datetime.datetime`):
            Date the action will be ended.

        min_bid (``int``):
            The minimum possible bid in the auction in Telegram Stars.

        bid_levels (List of :obj:`~pyrogram.types.AuctionBid`):
            A sparse list of bids that were made in the auction.

        top_bidder_user_ids (List of ``int``):
            User identifiers of at most 3 users with the biggest bids.

        rounds (List of :obj:`~pyrogram.types.AuctionRound`):
            Rounds of the auction in which their duration or extension rules are changed.

        current_round_end_date (:py:obj:`~datetime.datetime`):
            Date when the current round will end.

        current_round_number (``int``):
            1-based number of the current round.

        total_round_count (``int``):
            The total number of rounds.

        left_item_count (``int``):
            The number of items that have to be distributed on the auction.
    """

    def __init__(
        self,
        start_date: datetime,
        end_date: datetime,
        min_bid: int,
        bid_levels: List["types.AuctionBid"],
        top_bidder_user_ids: List[int],
        auction_rounds: List["types.AuctionRound"],
        current_round_end_date: datetime,
        current_round_number: int,
        total_round_count: int,
        left_item_count: int,
    ):
        super().__init__()

        self.start_date = start_date
        self.end_date = end_date
        self.min_bid = min_bid
        self.bid_levels = bid_levels
        self.top_bidder_user_ids = top_bidder_user_ids
        self.auction_rounds = auction_rounds
        self.current_round_end_date = current_round_end_date
        self.current_round_number = current_round_number
        self.total_round_count = total_round_count
        self.left_item_count = left_item_count

    @staticmethod
    async def _parse(auction_state: "raw.types.StarGiftAuctionState"):
        return AuctionStateActive(
            start_date=utils.timestamp_to_datetime(auction_state.start_date),
            end_date=utils.timestamp_to_datetime(auction_state.end_date),
            min_bid=auction_state.min_bid_amount,
            bid_levels=types.List(types.AuctionBid._parse(bid_level) for bid_level in auction_state.bid_levels),
            top_bidder_user_ids=auction_state.top_bidders,
            auction_rounds=types.List(
                types.AuctionRound._parse(auction_round) for auction_round in auction_state.rounds
            ),
            current_round_end_date=utils.timestamp_to_datetime(auction_state.next_round_at),
            current_round_number=auction_state.current_round,
            total_round_count=auction_state.total_rounds,
            left_item_count=auction_state.gifts_left,
        )


class AuctionStateFinished(AuctionState):
    """Contains information about a finished auction.

    Parameters:
        start_date (:py:obj:`~datetime.datetime`):
            Date the action was started.

        end_date (:py:obj:`~datetime.datetime`):
            Date the action will be ended.

        average_price (``int``):
            Average price of bought items in Telegram Stars.

        telegram_listed_item_count (``int``, *optional*):
            Number of items from the auction being resold on Telegram.

        fragment_listed_item_count (``int``, *optional*):
            Number of items from the auction being resold on Fragment.

        fragment_url (``str``, *optional*):
            The HTTPS link to the Fragment for the resold items.
            May be None if there are no such items being sold on Fragment.
    """

    def __init__(
        self,
        start_date: datetime,
        end_date: datetime,
        average_price: int,
        telegram_listed_item_count: Optional[int] = None,
        fragment_listed_item_count: Optional[int] = None,
        fragment_url: Optional[str] = None,
    ):
        super().__init__()

        self.start_date = start_date
        self.end_date = end_date
        self.average_price = average_price
        self.telegram_listed_item_count = telegram_listed_item_count
        self.fragment_listed_item_count = fragment_listed_item_count
        self.fragment_url = fragment_url

    @staticmethod
    async def _parse(
        auction_state: "raw.types.StarGiftAuctionStateFinished"
    ):
        return AuctionStateFinished(
            start_date=utils.timestamp_to_datetime(auction_state.start_date),
            end_date=utils.timestamp_to_datetime(auction_state.end_date),
            average_price=auction_state.average_price,
            telegram_listed_item_count=auction_state.listed_count,
            fragment_listed_item_count=auction_state.fragment_listed_count,
            fragment_url=auction_state.fragment_listed_url
        )
