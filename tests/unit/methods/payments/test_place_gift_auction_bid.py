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

import pytest

from pyrogram import raw
from pyrogram.methods.payments.place_gift_auction_bid import PlaceGiftAuctionBid


class _Parser:
    async def parse(self, text, mode=None):
        return {"message": text, "entities": []}


class FakeClient(PlaceGiftAuctionBid):
    """A client that records the raw `message` sent as part of the auction bid invoice."""

    def __init__(self) -> None:
        self.parse_mode = None
        self.parser = _Parser()
        self.written_message = None

    async def resolve_peer(self, peer_id):
        return raw.types.InputPeerSelf()

    async def invoke(self, query):
        if isinstance(query, raw.functions.payments.GetPaymentForm):
            self.written_message = query.invoice.message

            return raw.types.payments.PaymentForm(
                form_id=1,
                bot_id=1,
                title="Gift auction",
                description="",
                invoice=raw.types.Invoice(
                    currency="XTR",
                    prices=[raw.types.LabeledPrice(label="Gift", amount=100)],
                ),
                provider_id=1,
                url="",
                users=[],
            )

        return raw.types.payments.PaymentResult(updates=raw.types.UpdatesTooLong())


@pytest.mark.asyncio
async def test_bid_text_is_written_with_the_client() -> None:
    # FormattedText.write() requires `client`; calling it with no arguments raised
    #  `TypeError: write() missing 1 required positional argument` whenever bid text
    #  was actually provided.
    client = FakeClient()

    result = await client.place_gift_auction_bid(gift_id=1, star_count=100, text="hello")

    assert result is True
    assert isinstance(client.written_message, raw.types.TextWithEntities)
    assert client.written_message.text == "hello"


@pytest.mark.asyncio
async def test_no_text_skips_write() -> None:
    client = FakeClient()

    await client.place_gift_auction_bid(gift_id=1, star_count=100)

    assert client.written_message is None
