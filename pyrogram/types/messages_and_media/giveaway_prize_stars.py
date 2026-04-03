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
from typing import Dict, Optional

import pyrogram
from pyrogram import raw, types, utils
from pyrogram.errors import MessageIdsEmpty, ChannelPrivate

from ..object import Object


class GiveawayPrizeStars(Object):
    """A Telegram Stars were received by the current user from a giveaway.

    Parameters:
        star_count (``int``):
            Number of Telegram Stars that were gifted.

        transaction_id (``str``):
            Identifier of the transaction for Telegram Stars purchase.
            For receiver only

        boosted_chat (:obj:`~pyrogram.types.Chat`):
            Supergroup or channel chat, which was automatically boosted by the winners of the giveaway.

        giveaway_message_id (``int``):
            Identifier of the message with the giveaway in the boosted chat.

        giveaway_message (:obj:`~pyrogram.types.Message`, *optional*):
            Message with the giveaway in the boosted chat.

        is_unclaimed (``bool``, *optional*):
            True, if the corresponding winner wasn't chosen and the Telegram Stars were received by the owner of the boosted chat.

        sticker (:obj:`~pyrogram.types.Sticker`):
            A sticker to be shown in the message.
    """
    def __init__(
        self,
        *,
        star_count: int,
        transaction_id: str,
        boosted_chat: "types.Chat",
        giveaway_message_id: int,
        giveaway_message: Optional["types.Message"] = None,
        is_unclaimed: Optional[bool] = None,
        sticker: Optional["types.Sticker"] = None
    ):
        super().__init__()

        self.star_count = star_count
        self.transaction_id = transaction_id
        self.boosted_chat = boosted_chat
        self.giveaway_message_id = giveaway_message_id
        self.giveaway_message = giveaway_message
        self.is_unclaimed = is_unclaimed
        self.sticker = sticker

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        action: "raw.types.MessageActionPrizeStars",
        chats: Dict[int, "raw.base.Chat"],
    ) -> "GiveawayPrizeStars":
        raw_stickers = await client.invoke(
            raw.functions.messages.GetStickerSet(
                stickerset=raw.types.InputStickerSetPremiumGifts(),
                hash=0
            )
        )

        parsed_message = None

        try:
            parsed_message = await client.get_messages(
                chat_id=utils.get_peer_id(action.boost_peer),
                message_ids=action.giveaway_msg_id,
                replies=0
            )
        except (MessageIdsEmpty, ChannelPrivate):
            pass

        return GiveawayPrizeStars(
            star_count=action.stars,
            transaction_id=action.transaction_id,
            boosted_chat=types.Chat._parse_chat(client, chats.get(utils.get_raw_peer_id(action.boost_peer))),
            giveaway_message_id=action.giveaway_msg_id,
            giveaway_message=parsed_message,
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
