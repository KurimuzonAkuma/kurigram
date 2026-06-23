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
from pyrogram import enums, raw


class SendChatJoinRequestWebApp:
    async def send_chat_join_request_web_app(
        self: "pyrogram.Client",
        chat_join_request_query_id: str,
        web_app_url: str,
    ) -> bool:
        """Use this method to process a received chat join request query by showing a Mini App to the user before deciding the outcome.
        Call :meth:`~pyrogram.Client.answer_chat_join_request_query` to resolve the join request query based on the user interaction with the Mini App.

        .. include:: /_includes/usable-by/bots.rst

        Parameters:
            chat_join_request_query_id (``str``):
                Unique identifier of the join request query.

            web_app_url (``str``):
                The URL of the Mini App to be opened.

        Returns:
            ``bool``: On success True is returned.
        """
        return await self.invoke(
            raw.functions.bots.SetJoinChatResults(
                query_id=int(chat_join_request_query_id),
                result=raw.types.JoinChatBotResultWebView(url=web_app_url),
            )
        )
