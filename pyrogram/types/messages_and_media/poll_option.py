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

from typing import TYPE_CHECKING, List, Optional

from ..object import Object

if TYPE_CHECKING:
    import datetime

    import pyrogram
    from pyrogram import enums, types


class PollOption(Object):
    """Contains information about one answer option in a poll.

    Parameters:
        persistent_id (``str``):
            Unique identifier of the option, persistent on option addition and deletion.

        text (:obj:`~pyrogram.types.FormattedText`, *optional*):
            Option text, 1-100 characters.

        media (:obj:`~pyrogram.types.MessageContent`, *optional*):
            Option media.
            Currently, can be only of the types Animation, Location, Photo, Sticker, Venue, or Video without caption.

        voter_count (``int``, *optional*):
            Number of users that voted for this option.
            Equals to 0 until you vote.

        vote_percentage (``int``, *optional*):
            The percentage of votes for this option, 0-100.

        recent_voters (List of :obj:`~pyrogram.types.Chat`, *optional*):
            List of recent voters for the option, if the poll is non-anonymous and poll results are available.

        added_by_user (:obj:`~pyrogram.types.User`, *optional*):
            User who added the option.
            Omitted if the option wasn't added by a user after poll creation.

        added_by_chat (:obj:`~pyrogram.types.Chat`, *optional*):
            Chat that added the option.
            Omitted if the option wasn't added by a chat after poll creation.

        addition_date (:py:obj:`~datetime.datetime`, *optional*):
            Date when the option was added.
            Omitted if the option existed in the original poll.
    """

    def __init__(
        self,
        *,
        client: "pyrogram.Client" = None,
        persistent_id: str,
        text: Optional["types.FormattedText"] = None,
        media: Optional["types.MessageContent"] = None,
        voter_count: Optional[int] = None,
        vote_percentage: Optional[int] = None,
        recent_voters: Optional[List["types.Chat"]] = None,
        added_by_user: Optional["types.User"] = None,
        added_by_chat: Optional["types.Chat"] = None,
        addition_date: Optional["datetime.datetime"] = None,
    ):
        super().__init__(client)

        self.persistent_id = persistent_id
        self.text = text
        self.media = media
        self.voter_count = voter_count
        self.vote_percentage = vote_percentage
        self.recent_voters = recent_voters
        self.added_by_user = added_by_user
        self.added_by_chat = added_by_chat
        self.addition_date = addition_date
