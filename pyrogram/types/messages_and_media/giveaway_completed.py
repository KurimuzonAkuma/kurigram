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

from typing import Optional

import pyrogram

from pyrogram import raw, types, errors
from ..object import Object



class GiveawayCompleted(Object):
    """This object represents a service message about the completion of a giveaway without public winners.

    Parameters:
        winner_count (``int``):
            Number of winners in the giveaway.

        unclaimed_prize_count (``int``, *optional*):
            Number of undistributed prizes.

        giveaway_message_id (``int``, *optional*):
            Identifier of the message with the giveaway in the chat.

        giveaway_message (:obj:`~pyrogram.types.Message`, *optional*):
            Message with the giveaway that was completed, if it wasn't deleted.

        is_star_giveaway (``bool``, *optional*):
            True, if the giveaway is a Telegram Star giveaway. Otherwise, currently, the giveaway is a Telegram Premium giveaway.

    """

    def __init__(
        self,
        *,
        client: Optional["pyrogram.Client"] = None,
        winner_count: int,
        unclaimed_prize_count: Optional[int] = None,
        giveaway_message_id: Optional[int] = None,
        giveaway_message: Optional["types.Message"] = None,
        is_star_giveaway: Optional[bool] = None
    ):
        super().__init__(client)

        self.winner_count = winner_count
        self.unclaimed_prize_count = unclaimed_prize_count
        self.giveaway_message_id = giveaway_message_id
        self.giveaway_message = giveaway_message
        self.is_star_giveaway = is_star_giveaway


    @staticmethod
    async def _parse(
        client,
        giveaway_results: "raw.types.MessageActionGiveawayResults",
        chat: Optional["types.Chat"] = None,
        message_id: Optional[int] = None
    ) -> "GiveawayCompleted":
        if not isinstance(giveaway_results, raw.types.MessageActionGiveawayResults):
            return

        giveaway_message = None

        if chat and message_id:
            try:
                giveaway_message = await client.get_messages(
                    chat_id=chat.id,
                    message_ids=message_id,
                    replies=0
                )
            except (errors.ChannelPrivate, errors.ChannelInvalid):
                pass

        return GiveawayCompleted(
            winner_count=giveaway_results.winners_count,
            unclaimed_prize_count=giveaway_results.unclaimed_count,
            giveaway_message_id=message_id,
            giveaway_message=giveaway_message,
            is_star_giveaway=getattr(giveaway_results, "stars", None),
            client=client,
        )
