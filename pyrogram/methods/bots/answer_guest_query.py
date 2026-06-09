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

import pyrogram
from pyrogram import raw, types


class AnswerGuestQuery:
    async def answer_guest_query(
        self: "pyrogram.Client", guest_query_id: str, result: "types.InlineQueryResult"
    ):
        """Use this method to reply to a received guest message.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            guest_query_id (``str``):
                Unique identifier for the answered query.

            result (:obj:`~pyrogram.types.InlineQueryResult`):
                A result for the guest query.

        Returns:
            :obj:`~pyrogram.types.SentGuestMessage`: On success, a :obj:`~pyrogram.types.SentGuestMessage` object is returned.

        Example:
            .. code-block:: python

                from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent

                await app.answer_guest_query(
                    guest_query_id,
                    result=InlineQueryResultArticle(
                        "Title",
                        InputTextMessageContent("Message content")
                    ),
                )
        """
        r = await self.invoke(
            raw.functions.messages.SetBotGuestChatResult(
                query_id=int(guest_query_id),
                result=await result.write(self),
            )
        )

        return await types.SentGuestMessage._parse(r)
