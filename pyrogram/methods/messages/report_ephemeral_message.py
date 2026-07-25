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

from typing import Union

import pyrogram
from pyrogram import raw


class ReportEphemeralMessage:
    async def report_ephemeral_message(
        self: "pyrogram.Client",
        chat_id: Union[int, str],
        message_id: int,
        option: bytes,
        message: str = "",
    ) -> "raw.base.ReportResult":
        """Report an ephemeral message for violating Telegram's Terms of Service.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_id (``int`` | ``str``):
                Unique identifier (int) or username (str) of the target chat.

            message_id (``int``):
                Identifier of the ephemeral message to report.

            option (``bytes``):
                The option chosen from a previously received :obj:`~pyrogram.raw.base.ReportResult`.
                Pass an empty ``bytes`` object to obtain the initial set of options.

            message (``str``, *optional*):
                An optional free-form message describing the report.

        Returns:
            :obj:`~pyrogram.raw.base.ReportResult`: The follow-up report options, or the final
            report result.

        Example:
            .. code-block:: python

                await app.report_ephemeral_message(chat_id, message_id, option=b"")
        """
        return await self.invoke(
            raw.functions.ephemeral.ReportMessage(
                peer=await self.resolve_peer(chat_id),
                id=message_id,
                option=option,
                message=message,
            )
        )
