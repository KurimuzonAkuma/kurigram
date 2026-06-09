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
from pyrogram import raw, types

from ..object import Object


class PollOptionDeleted(Object):
    """Describes a service message about an option deleted from a poll.

    Parameters:
        poll_message (:obj:`~pyrogram.types.Message`, *optional*):
            Message containing the poll from which the option was deleted, if known.

        option_persistent_id (``str``):
            Unique identifier of the deleted option.

        text (:obj:`~pyrogram.types.FormattedText`, *optional*):
            Option text.
    """

    def __init__(
        self,
        *,
        poll_message: Optional["types.Message"] = None,
        option_persistent_id: str,
        text: "types.FormattedText"
    ):
        super().__init__()

        self.poll_message = poll_message
        self.option_persistent_id = option_persistent_id
        self.text = text

    @staticmethod
    async def _parse(
        client: "pyrogram.Client",
        reply_message: Optional["types.Message"],
        poll_option_deleted: "raw.types.MessageActionPollDeleteAnswer",
    ) -> "PollOptionDeleted":
        if not isinstance(poll_option_deleted, raw.types.MessageActionPollDeleteAnswer):
            return

        answer = poll_option_deleted.answer

        return PollOptionDeleted(
            poll_message=reply_message,
            option_persistent_id=answer.option.decode(),
            text=types.FormattedText._parse(client, answer.text)
        )
